// Load environment variables first
require('dotenv').config();

const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs-extra');
const cors = require('cors');
const { transcribeAudio } = require('./services/speechToText');
const { generateSlides } = require('./services/slideGenerator');
const { createPresentation } = require('./services/presentationBuilder');
const { exportToPDF } = require('./services/pdfExporter');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));
app.use('/presentations', express.static('presentations'));

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    fs.ensureDirSync('uploads');
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    const allowedTypes = /mp3|wav|m4a|ogg|webm|mp4/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only audio files are allowed'));
    }
  },
  limits: {
    fileSize: 50 * 1024 * 1024 // 50MB limit
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

app.post('/api/upload-audio', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No audio file uploaded' });
    }

    const audioPath = req.file.path;
    const sessionId = Date.now().toString();
    
    console.log('Processing audio file:', audioPath);
    
    // Step 1: Transcribe audio to text
    const transcript = await transcribeAudio(audioPath);
    console.log('Transcription completed');
    
    // Step 2: Generate slide content from transcript
    const slideContent = await generateSlides(transcript);
    console.log('Slide content generated');
    
    // Step 3: Create HTML presentation
    const presentationPath = await createPresentation(slideContent, sessionId);
    console.log('HTML presentation created');
    
    // Step 4: Generate PDF
    const pdfPath = await exportToPDF(presentationPath, sessionId);
    console.log('PDF exported');
    
    // Clean up uploaded audio file
    await fs.remove(audioPath);
    
    res.json({
      success: true,
      sessionId: sessionId,
      htmlUrl: `/presentations/${sessionId}/presentation.html`,
      pdfUrl: `/presentations/${sessionId}/presentation.pdf`,
      slideCount: slideContent.slides.length,
      transcript: transcript
    });
    
  } catch (error) {
    console.error('Error processing audio:', error);
    res.status(500).json({ error: 'Failed to process audio file: ' + error.message });
  }
});

app.get('/api/presentation/:sessionId', async (req, res) => {
  try {
    const { sessionId } = req.params;
    const presentationDir = path.join(__dirname, '../presentations', sessionId);
    
    if (!await fs.pathExists(presentationDir)) {
      return res.status(404).json({ error: 'Presentation not found' });
    }
    
    const htmlPath = path.join(presentationDir, 'presentation.html');
    const pdfPath = path.join(presentationDir, 'presentation.pdf');
    
    res.json({
      sessionId: sessionId,
      htmlUrl: `/presentations/${sessionId}/presentation.html`,
      pdfUrl: `/presentations/${sessionId}/presentation.pdf`,
      htmlExists: await fs.pathExists(htmlPath),
      pdfExists: await fs.pathExists(pdfPath)
    });
    
  } catch (error) {
    console.error('Error retrieving presentation:', error);
    res.status(500).json({ error: 'Failed to retrieve presentation' });
  }
});

app.listen(PORT, () => {
  console.log(`Voice-to-Slide Generator running on port ${PORT}`);
  console.log(`Visit http://localhost:${PORT} to use the application`);
});

module.exports = app;