const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs-extra');

async function exportToPDF(htmlPath, sessionId) {
  let browser = null;
  
  try {
    console.log('Starting PDF export for:', htmlPath);
    
    if (!await fs.pathExists(htmlPath)) {
      throw new Error('HTML presentation file not found: ' + htmlPath);
    }
    
    // Launch browser with optimized settings for Cloud Run
    browser = await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-accelerated-2d-canvas',
        '--disable-gpu',
        '--disable-web-security',
        '--disable-features=IsolateOrigins',
        '--disable-site-isolation-trials',
        '--no-first-run',
        '--no-zygote',
        '--single-process',
        '--disable-blink-features=AutomationControlled',
        '--window-size=1920,1080',
        '--user-data-dir=/tmp/.chrome',
        '--data-path=/tmp/.chrome'
      ],
      // Use system Chrome when available (for Docker/Cloud Run)
      executablePath: process.env.PUPPETEER_EXECUTABLE_PATH || '/usr/bin/google-chrome-stable',
      // Increase timeout for slow Cloud Run starts
      timeout: 60000
    });
    
    const page = await browser.newPage();
    
    // Set viewport for consistent rendering
    await page.setViewport({
      width: 1920,
      height: 1080,
      deviceScaleFactor: 2
    });
    
    // Load the HTML file
    const fileUrl = 'file://' + htmlPath;
    await page.goto(fileUrl, { 
      waitUntil: 'networkidle0',
      timeout: 30000 
    });
    
    // Wait for the presentation to fully load
    await page.waitForSelector('.slide.active', { timeout: 10000 });
    
    // Get slide count
    const slideCount = await page.evaluate(() => {
      return document.querySelectorAll('.slide').length;
    });
    
    console.log(`Exporting ${slideCount} slides to PDF...`);
    
    // Hide navigation and controls for PDF
    await page.addStyleTag({
      content: `
        .navigation, .controls, .slide-counter, .progress-bar {
          display: none !important;
        }
        .slide {
          margin: 0 !important;
          width: 100% !important;
          height: 100vh !important;
          display: flex !important;
          page-break-after: always;
        }
        .slide:last-child {
          page-break-after: avoid;
        }
        body {
          background: white !important;
        }
        .slide-notes {
          background: #f8f9fa !important;
          -webkit-print-color-adjust: exact !important;
          print-color-adjust: exact !important;
        }
      `
    });
    
    // Show all slides for PDF export
    await page.evaluate(() => {
      const slides = document.querySelectorAll('.slide');
      slides.forEach(slide => {
        slide.classList.add('active');
        slide.style.display = 'flex';
      });
    });
    
    // Generate PDF
    const pdfPath = path.join(path.dirname(htmlPath), 'presentation.pdf');
    
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      landscape: true,
      printBackground: true,
      margin: {
        top: '20px',
        bottom: '20px',
        left: '20px',
        right: '20px'
      },
      displayHeaderFooter: false,
      preferCSSPageSize: false
    });
    
    console.log('PDF exported successfully to:', pdfPath);
    return pdfPath;
    
  } catch (error) {
    console.error('Error exporting PDF:', error);
    throw new Error('Failed to export PDF: ' + error.message);
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Alternative PDF export using a simpler approach
async function exportToPDFSimple(htmlPath, sessionId) {
  let browser = null;
  
  try {
    console.log('Using simple PDF export for:', htmlPath);
    
    browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    const page = await browser.newPage();
    
    const htmlContent = await fs.readFile(htmlPath, 'utf8');
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
    
    const pdfPath = path.join(path.dirname(htmlPath), 'presentation.pdf');
    
    await page.pdf({
      path: pdfPath,
      format: 'A4',
      landscape: true,
      printBackground: true
    });
    
    console.log('Simple PDF export completed:', pdfPath);
    return pdfPath;
    
  } catch (error) {
    console.error('Error in simple PDF export:', error);
    throw error;
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// Fallback PDF generation using HTML-to-text conversion
async function generatePDFFallback(slideData, sessionId) {
  try {
    console.log('Using fallback PDF generation method');
    
    const presentationDir = path.join(__dirname, '../../presentations', sessionId);
    await fs.ensureDir(presentationDir);
    
    // Create a simple text-based version for PDF
    const textContent = generateTextPresentation(slideData);
    const textPath = path.join(presentationDir, 'presentation.txt');
    await fs.writeFile(textPath, textContent, 'utf8');
    
    // Create a simple HTML version optimized for PDF
    const simpleHTML = generateSimplePDFHTML(slideData);
    const htmlPath = path.join(presentationDir, 'presentation_pdf.html');
    await fs.writeFile(htmlPath, simpleHTML, 'utf8');
    
    // Try to convert to PDF
    const pdfPath = await exportToPDFSimple(htmlPath, sessionId);
    
    // Clean up temporary HTML file
    await fs.remove(htmlPath);
    
    return pdfPath;
    
  } catch (error) {
    console.error('Fallback PDF generation failed:', error);
    throw error;
  }
}

function generateTextPresentation(slideData) {
  const { title, slides } = slideData;
  
  let content = `${title.toUpperCase()}\n`;
  content += '='.repeat(title.length) + '\n\n';
  
  slides.forEach((slide, index) => {
    content += `SLIDE ${index + 1}: ${slide.title.toUpperCase()}\n`;
    content += '-'.repeat(50) + '\n\n';
    
    slide.content.forEach(point => {
      content += `• ${point}\n`;
    });
    
    content += '\nSPEAKER NOTES:\n';
    content += slide.speakerNotes + '\n\n';
    content += '\n' + '='.repeat(50) + '\n\n';
  });
  
  return content;
}

function generateSimplePDFHTML(slideData) {
  const { title, slides } = slideData;
  
  const slideHTML = slides.map((slide, index) => `
    <div class="pdf-slide">
      <h1>${slide.title}</h1>
      <div class="content">
        ${slide.content.map(point => `<div class="bullet">• ${point}</div>`).join('')}
      </div>
      <div class="speaker-notes">
        <h3>Speaker Notes:</h3>
        <p>${slide.speakerNotes}</p>
      </div>
      <div class="slide-number">Slide ${index + 1} of ${slides.length}</div>
    </div>
    ${index < slides.length - 1 ? '<div class="page-break"></div>' : ''}
  `).join('');

  return `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>${title}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        .pdf-slide {
            min-height: 90vh;
            padding: 40px;
            border: 1px solid #ddd;
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        .content {
            margin: 30px 0;
        }
        .bullet {
            margin: 15px 0;
            font-size: 16px;
        }
        .speaker-notes {
            background: #f5f5f5;
            padding: 20px;
            border-left: 4px solid #667eea;
            margin-top: 40px;
        }
        .speaker-notes h3 {
            margin-top: 0;
            color: #333;
        }
        .slide-number {
            text-align: right;
            color: #666;
            margin-top: 20px;
        }
        .page-break {
            page-break-after: always;
        }
        @media print {
            .pdf-slide {
                border: none;
                margin: 0;
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    ${slideHTML}
</body>
</html>`;
}

module.exports = { 
  exportToPDF, 
  exportToPDFSimple, 
  generatePDFFallback 
};