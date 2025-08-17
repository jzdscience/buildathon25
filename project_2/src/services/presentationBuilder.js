const fs = require('fs-extra');
const path = require('path');

async function createPresentation(slideData, sessionId) {
  try {
    console.log('Creating HTML presentation...');
    
    const presentationDir = path.join(__dirname, '../../presentations', sessionId);
    await fs.ensureDir(presentationDir);
    
    const htmlContent = generateHTMLPresentation(slideData);
    const presentationPath = path.join(presentationDir, 'presentation.html');
    
    await fs.writeFile(presentationPath, htmlContent, 'utf8');
    
    console.log('HTML presentation created at:', presentationPath);
    return presentationPath;
    
  } catch (error) {
    console.error('Error creating presentation:', error);
    throw new Error('Failed to create presentation: ' + error.message);
  }
}

function generateHTMLPresentation(slideData) {
  const { title, slides } = slideData;
  
  const slideHTML = slides.map((slide, index) => `
    <section class="slide ${index === 0 ? 'active' : ''}" data-slide="${index}">
      <div class="slide-content">
        <h1 class="slide-title">${escapeHtml(slide.title)}</h1>
        ${slide.slideNumber === 1 ? 
          `<div class="title-slide-content">
            <p class="subtitle">A comprehensive overview</p>
            <div class="title-bullets">
              ${slide.content.map(point => `<div class="title-bullet">• ${escapeHtml(point)}</div>`).join('')}
            </div>
          </div>` :
          `<div class="slide-bullets">
            ${slide.content.map(point => `<div class="bullet-point">• ${escapeHtml(point)}</div>`).join('')}
          </div>`
        }
      </div>
      <div class="slide-notes">
        <h3>Speaker Notes</h3>
        <p>${escapeHtml(slide.speakerNotes)}</p>
      </div>
      <div class="slide-number">${slide.slideNumber} / ${slides.length}</div>
    </section>
  `).join('');

  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${escapeHtml(title)}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            overflow: hidden;
            height: 100vh;
        }

        .presentation-container {
            position: relative;
            width: 100%;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .slide {
            display: none;
            width: 90%;
            max-width: 1200px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            padding: 60px;
            position: relative;
            animation: slideIn 0.5s ease-in-out;
        }

        .slide.active {
            display: flex;
            flex-direction: column;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        .slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .slide-title {
            font-size: 3em;
            color: #333;
            margin-bottom: 40px;
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            font-weight: 700;
        }

        .title-slide-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }

        .subtitle {
            font-size: 1.5em;
            color: #666;
            margin-bottom: 40px;
            font-style: italic;
        }

        .title-bullets {
            max-width: 800px;
        }

        .title-bullet {
            font-size: 1.3em;
            margin: 20px 0;
            color: #555;
            line-height: 1.6;
        }

        .slide-bullets {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 40px 0;
        }

        .bullet-point {
            font-size: 1.4em;
            margin: 25px 0;
            line-height: 1.8;
            color: #444;
            position: relative;
            padding-left: 30px;
        }

        .bullet-point::before {
            content: "•";
            color: #667eea;
            font-size: 1.5em;
            position: absolute;
            left: 0;
            top: 0;
        }

        .slide-notes {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 30px;
            border-left: 4px solid #667eea;
            max-height: 150px;
            overflow-y: auto;
        }

        .slide-notes h3 {
            color: #333;
            margin-bottom: 10px;
            font-size: 1.1em;
        }

        .slide-notes p {
            color: #666;
            line-height: 1.5;
            font-size: 0.95em;
        }

        .slide-number {
            position: absolute;
            bottom: 20px;
            right: 30px;
            color: #888;
            font-size: 1em;
            font-weight: 500;
        }

        .navigation {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 20px;
            z-index: 1000;
        }

        .nav-btn {
            background: rgba(255, 255, 255, 0.9);
            border: none;
            border-radius: 50px;
            padding: 15px 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            color: #333;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .nav-btn:hover:not(:disabled) {
            background: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }

        .nav-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: #667eea;
            transition: width 0.3s ease;
            z-index: 1001;
        }

        .controls {
            position: fixed;
            top: 30px;
            right: 30px;
            display: flex;
            gap: 15px;
            z-index: 1000;
        }

        .control-btn {
            background: rgba(255, 255, 255, 0.9);
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.2em;
            color: #333;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }

        .control-btn:hover {
            background: white;
            transform: scale(1.1);
        }

        .fullscreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 2000;
        }

        .notes-visible .slide-notes {
            display: block;
        }

        .notes-hidden .slide-notes {
            display: none;
        }

        .slide-counter {
            position: fixed;
            top: 30px;
            left: 30px;
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            color: #333;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
            z-index: 1000;
        }

        @media (max-width: 768px) {
            .slide {
                width: 95%;
                height: 85vh;
                padding: 30px;
            }

            .slide-title {
                font-size: 2em;
                margin-bottom: 30px;
            }

            .bullet-point {
                font-size: 1.1em;
                margin: 15px 0;
            }

            .title-bullet {
                font-size: 1.1em;
                margin: 15px 0;
            }

            .navigation {
                bottom: 20px;
                gap: 10px;
            }

            .nav-btn {
                padding: 12px 20px;
                font-size: 0.9em;
            }

            .controls {
                top: 20px;
                right: 20px;
                gap: 10px;
            }

            .control-btn {
                width: 40px;
                height: 40px;
                font-size: 1em;
            }
        }

        @media print {
            body {
                background: white;
            }

            .slide {
                display: block !important;
                width: 100%;
                height: auto;
                margin: 0 0 50px 0;
                padding: 40px;
                border: 1px solid #ddd;
                border-radius: 0;
                box-shadow: none;
                page-break-after: always;
            }

            .navigation, .controls, .slide-counter {
                display: none;
            }

            .progress-bar {
                display: none;
            }
        }
    </style>
</head>
<body class="notes-visible">
    <div class="presentation-container">
        <div class="progress-bar" id="progressBar"></div>
        
        <div class="slide-counter">
            <span id="currentSlide">1</span> / <span id="totalSlides">${slides.length}</span>
        </div>
        
        <div class="controls">
            <button class="control-btn" id="notesToggle" title="Toggle Speaker Notes">📝</button>
            <button class="control-btn" id="fullscreenBtn" title="Toggle Fullscreen">⛶</button>
            <button class="control-btn" onclick="window.print()" title="Print Slides">🖨️</button>
        </div>
        
        ${slideHTML}
        
        <div class="navigation">
            <button class="nav-btn" id="prevBtn">← Previous</button>
            <button class="nav-btn" id="nextBtn">Next →</button>
        </div>
    </div>

    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const progressBar = document.getElementById('progressBar');
        const currentSlideDisplay = document.getElementById('currentSlide');
        const notesToggle = document.getElementById('notesToggle');
        const fullscreenBtn = document.getElementById('fullscreenBtn');

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
            });
            
            currentSlide = index;
            currentSlideDisplay.textContent = index + 1;
            
            prevBtn.disabled = index === 0;
            nextBtn.disabled = index === totalSlides - 1;
            
            const progress = ((index + 1) / totalSlides) * 100;
            progressBar.style.width = progress + '%';
        }

        function nextSlide() {
            if (currentSlide < totalSlides - 1) {
                showSlide(currentSlide + 1);
            }
        }

        function prevSlide() {
            if (currentSlide > 0) {
                showSlide(currentSlide - 1);
            }
        }

        // Event listeners
        nextBtn.addEventListener('click', nextSlide);
        prevBtn.addEventListener('click', prevSlide);

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowRight':
                case ' ':
                    e.preventDefault();
                    nextSlide();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    prevSlide();
                    break;
                case 'Home':
                    e.preventDefault();
                    showSlide(0);
                    break;
                case 'End':
                    e.preventDefault();
                    showSlide(totalSlides - 1);
                    break;
                case 'n':
                case 'N':
                    toggleNotes();
                    break;
                case 'f':
                case 'F':
                    toggleFullscreen();
                    break;
            }
        });

        // Notes toggle
        notesToggle.addEventListener('click', toggleNotes);
        
        function toggleNotes() {
            document.body.classList.toggle('notes-visible');
            document.body.classList.toggle('notes-hidden');
        }

        // Fullscreen toggle
        fullscreenBtn.addEventListener('click', toggleFullscreen);
        
        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen();
            } else {
                document.exitFullscreen();
            }
        }

        // Initialize
        showSlide(0);

        // Auto-advance slides (optional - uncomment to enable)
        // setInterval(() => {
        //     if (currentSlide < totalSlides - 1) {
        //         nextSlide();
        //     }
        // }, 10000); // Auto-advance every 10 seconds
        
        console.log('Presentation loaded with', totalSlides, 'slides');
        console.log('Keyboard shortcuts:');
        console.log('- Arrow keys or Space: Navigate slides');
        console.log('- N: Toggle speaker notes');
        console.log('- F: Toggle fullscreen');
        console.log('- Home/End: Go to first/last slide');
    </script>
</body>
</html>`;
}

function escapeHtml(text) {
  const div = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  return text.replace(/[&<>"']/g, (match) => div[match]);
}

module.exports = { createPresentation };