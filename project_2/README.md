# 🎤 Voice-to-Slide Generator

Transform your spoken ideas into professional presentations in minutes! This application converts 3-minute audio recordings into polished slide decks with speaker notes, available as both HTML presentations and PDF downloads.

## ✨ Features

- **Audio Input Options**: Upload audio files or record directly in the browser
- **AI-Powered Generation**: Uses OpenAI's Whisper for transcription and GPT-4 for slide generation
- **Professional Output**: Creates 5-8 slides with comprehensive speaker notes
- **Multiple Formats**: Exports as interactive HTML presentations and PDF files
- **Interactive Presentation**: Navigate with keyboard shortcuts, toggle speaker notes, fullscreen mode
- **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- OpenAI API key (get one at [platform.openai.com](https://platform.openai.com/api-keys))

### Installation

1. **Clone and setup**:
   ```bash
   cd project_1
   npm install
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Start the application**:
   ```bash
   npm start
   ```

4. **Open your browser**: Navigate to `http://localhost:3000`

## 🎯 How to Use

### Option 1: Upload Audio File
1. Click "Choose Audio File" or drag & drop an audio file
2. Supported formats: MP3, WAV, M4A, OGG, WebM, MP4
3. Maximum file size: 50MB (~3 minutes recommended)

### Option 2: Record Audio
1. Click "🎙️ Start Recording"
2. Allow microphone access when prompted
3. Speak for up to 3 minutes
4. Click "⏹️ Stop Recording"

### Results
- **HTML Presentation**: Interactive slides with navigation and speaker notes
- **PDF Download**: Printable version with all slides and notes
- **Transcript**: Full text transcription of your audio

## 🎮 Presentation Controls

### Keyboard Shortcuts
- **Arrow Keys / Space**: Navigate slides
- **N**: Toggle speaker notes visibility
- **F**: Toggle fullscreen mode
- **Home/End**: Jump to first/last slide

### Mouse Controls
- **Previous/Next buttons**: Navigate slides
- **📝**: Toggle speaker notes
- **⛶**: Toggle fullscreen
- **🖨️**: Print slides

## 📁 Project Structure

```
voice-to-slide-generator/
├── src/
│   ├── app.js                 # Main Express server
│   └── services/
│       ├── speechToText.js    # OpenAI Whisper integration
│       ├── slideGenerator.js  # GPT-4 slide generation
│       ├── presentationBuilder.js # HTML presentation creation
│       └── pdfExporter.js     # PDF export using Puppeteer
├── public/
│   └── index.html            # Web interface
├── uploads/                  # Temporary audio files
├── presentations/            # Generated presentations
└── package.json
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PORT`: Server port (default: 3000)
- `NODE_ENV`: Environment (development/production)

### Audio Requirements
- **Duration**: ~3 minutes recommended (optimal for slide generation)
- **Quality**: Clear speech, minimal background noise
- **Language**: English (optimized for English content)

## 🎨 Slide Generation Process

1. **Audio Processing**: Upload/record audio file
2. **Transcription**: Convert speech to text using OpenAI Whisper
3. **Content Analysis**: Analyze transcript and extract key topics
4. **Slide Creation**: Generate 5-8 structured slides with bullet points
5. **Speaker Notes**: Create detailed presenter notes for each slide
6. **Export**: Generate HTML presentation and PDF file

## 🐳 Docker Deployment

### Local Docker Testing
```bash
# Build the Docker image
docker build -t voice-to-slide-generator .

# Run the container locally
docker run -p 8080:8080 \
  -e OPENAI_API_KEY="your-api-key" \
  voice-to-slide-generator
```

## ☁️ Google Cloud Run Deployment

### Prerequisites
- Google Cloud account with billing enabled
- Google Cloud SDK (`gcloud`) installed
- Docker installed (for local builds)
- OpenAI API key

### Quick Deployment

1. **Clone the repository and navigate to project**:
   ```bash
   cd /home/ipsoct4/buildathon2025/project_2
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```
   The script will:
   - Enable required Google Cloud APIs
   - Store your OpenAI API key securely in Google Secret Manager
   - Build and deploy the container to Cloud Run
   - Provide you with the service URL

### Manual Deployment

1. **Set your Google Cloud project**:
   ```bash
   export PROJECT_ID="your-project-id"
   gcloud config set project $PROJECT_ID
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     containerregistry.googleapis.com \
     secretmanager.googleapis.com
   ```

3. **Create OpenAI API key secret**:
   ```bash
   echo -n "your-openai-api-key" | gcloud secrets create openai-api-key \
     --data-file=- \
     --replication-policy="automatic"
   ```

4. **Deploy using Cloud Build**:
   ```bash
   gcloud builds submit --config=cloudbuild.yaml
   ```

   Or build and deploy manually:
   ```bash
   # Build and push image
   docker build -t gcr.io/$PROJECT_ID/voice-to-slide-generator .
   gcloud auth configure-docker
   docker push gcr.io/$PROJECT_ID/voice-to-slide-generator

   # Deploy to Cloud Run
   gcloud run deploy voice-to-slide-generator \
     --image gcr.io/$PROJECT_ID/voice-to-slide-generator \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --update-secrets OPENAI_API_KEY=openai-api-key:latest
   ```

### Cloud Run Configuration

The application is configured with:
- **Memory**: 2Gi (required for Puppeteer/Chrome)
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds (5 minutes)
- **Min instances**: 0 (scales to zero)
- **Max instances**: 10 (auto-scaling)

### Managing Secrets

Update your OpenAI API key:
```bash
echo -n "new-api-key" | gcloud secrets versions add openai-api-key --data-file=-
```

### Monitoring and Logs

View application logs:
```bash
gcloud run services logs read voice-to-slide-generator --region=us-central1
```

Monitor in Cloud Console:
```bash
gcloud run services describe voice-to-slide-generator --region=us-central1
```

### Cost Optimization

- The service scales to zero when not in use (no charges)
- You're only charged for actual usage (requests and compute time)
- Estimated costs:
  - Idle: $0/month
  - Light usage (100 requests/month): ~$1-2/month
  - Heavy usage (1000+ requests/month): ~$10-20/month

## 🛠️ Development

### Scripts
```bash
npm start          # Start production server
npm run dev        # Start development server with nodemon
npm test          # Run tests
```

### API Endpoints
- `POST /api/upload-audio`: Process audio file and generate presentation
- `GET /api/presentation/:sessionId`: Retrieve presentation info

## 🎯 Use Cases

- **Business Presentations**: Convert meeting recordings to slide decks
- **Educational Content**: Transform lectures into structured slides
- **Conference Talks**: Quickly create presentation materials
- **Training Materials**: Convert spoken content to visual presentations
- **Pitch Decks**: Transform verbal pitches into professional slides

## 🔒 Security & Privacy

- Audio files are processed locally and deleted after conversion
- No audio data is permanently stored
- API keys are secured through environment variables
- Generated presentations are temporarily stored and can be cleaned up

## 🚨 Troubleshooting

### Common Issues

**Audio upload fails**:
- Check file format (MP3, WAV, M4A, OGG, WebM, MP4)
- Ensure file size is under 50MB
- Verify audio quality and clarity

**Transcription errors**:
- Ensure clear speech with minimal background noise
- Check OpenAI API key configuration
- Verify API quota and billing status

**PDF generation fails**:
- Check available disk space
- Ensure Puppeteer can access system fonts
- Try refreshing and regenerating

### Error Messages
- `"No speech detected"`: Audio may be too quiet or unclear
- `"API quota exceeded"`: Check OpenAI billing and usage limits
- `"Invalid API key"`: Verify OPENAI_API_KEY in .env file

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions welcome! Please feel free to submit issues and enhancement requests.

---

**Made with ❤️ for the Buildathon 2025**

Transform your voice into professional presentations in minutes!