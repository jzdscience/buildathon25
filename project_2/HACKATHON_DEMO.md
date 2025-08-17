# 🏆 Hackathon Demo Quick Setup

## 🚀 Fastest Setup (2 minutes)

### Option 1: Interactive Setup (Recommended)
```bash
./setup-demo.sh
```
This will:
1. Ask for your OpenAI API key
2. Create the `.env` file automatically
3. Set up your chosen demo environment

### Option 2: Manual Quick Setup

1. **Create `.env` file** with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
echo "PORT=3000" >> .env
echo "NODE_ENV=production" >> .env
```

2. **Choose your demo platform:**

#### 🏠 Local Demo (Fastest)
```bash
npm install
npm start
# Open http://localhost:3000
```

#### 🐳 Docker Demo (Most Reliable)
```bash
docker-compose up
# Open http://localhost:8080
```

#### ☁️ Cloud Run Demo (Most Impressive)
```bash
# Set your project ID
export GCP_PROJECT_ID="your-project-id"

# Deploy
./redeploy.sh
```

## 📝 OpenAI API Key

### Get Your API Key:
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### Important for Hackathon:
- ✅ Make sure your API key has credits
- ✅ Test it before the demo
- ✅ Keep a backup key ready
- ⚠️ Never share or commit your API key

## 🎯 Demo Script

### 1. Show the Problem
"Converting spoken ideas into presentations is time-consuming"

### 2. Live Demo
```
1. Click "Start Recording" or upload a pre-recorded audio
2. Speak for 1-2 minutes about any topic
3. Click "Generate Slides"
4. Show the generated HTML presentation
5. Download the PDF version
```

### 3. Key Features to Highlight
- **AI-Powered**: Uses OpenAI Whisper + GPT-4
- **Multi-format**: HTML and PDF output
- **Professional**: 5-8 slides with speaker notes
- **Fast**: Under 30 seconds processing time

## 🎤 Sample Demo Topics

Quick 1-minute recordings that work well:
1. "The importance of renewable energy"
2. "How to build a successful startup"
3. "The future of artificial intelligence"
4. "Benefits of remote work"
5. "Introduction to blockchain technology"

## 🔥 Pro Tips for Demo Day

### Before the Demo:
```bash
# 1. Test your setup
./setup-demo.sh
npm start

# 2. Pre-record a backup audio file
# Save a 1-2 minute MP3 as backup

# 3. Clear old presentations
rm -rf presentations/* uploads/*

# 4. Test your API key
node -e "console.log('API Key:', process.env.OPENAI_API_KEY ? '✓ Set' : '✗ Missing')"
```

### During the Demo:
- Have a backup audio file ready
- Use clear, structured speech
- Keep recordings to 1-2 minutes
- Show both HTML and PDF outputs
- Navigate slides with arrow keys

### If Something Goes Wrong:
1. Use your pre-recorded audio file
2. Have screenshots/video as backup
3. Check the browser console for errors
4. Restart the service if needed

## 🛠️ Troubleshooting

### API Key Issues:
```bash
# Check if API key is set
cat .env | grep OPENAI_API_KEY

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $(grep OPENAI_API_KEY .env | cut -d'=' -f2)"
```

### Docker Issues:
```bash
# Rebuild if needed
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Port Already in Use:
```bash
# Change port in .env
echo "PORT=3001" >> .env
# Or kill the process using the port
lsof -ti:3000 | xargs kill -9
```

## 📊 Performance Stats to Mention

- **Processing Time**: ~20-30 seconds
- **Audio Support**: 3+ minutes, multiple formats
- **Output Quality**: Professional-grade slides
- **Scalability**: Cloud Run auto-scales to handle load
- **Cost**: < $0.10 per presentation

## 🎬 Demo Flow (3 minutes)

```
0:00 - Problem statement
0:30 - Show the app interface
1:00 - Record/upload audio
1:30 - Generate slides (processing)
2:00 - Show HTML presentation
2:30 - Download PDF
2:45 - Q&A ready
```

## 🔐 Security Notes

### For the Hackathon:
- ✅ Use a demo API key with limited credits
- ✅ Don't show your API key on screen
- ✅ Clear browser history after demo
- ✅ Rotate API key after the event

### Add to .gitignore:
```bash
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

## 📱 Quick Commands Reference

```bash
# Setup
./setup-demo.sh

# Run locally
npm start

# Run with Docker
docker-compose up

# Deploy to Cloud Run
./redeploy.sh

# Check logs
docker-compose logs -f              # Docker
gcloud run services logs tail voice-to-slide-generator  # Cloud Run

# Clean up
rm -rf presentations/* uploads/*    # Clear generated files
docker-compose down                 # Stop Docker
```

## 🏆 Winning Tips

1. **Practice the demo** at least 3 times
2. **Have backups** (recordings, screenshots)
3. **Keep it simple** - focus on the magic
4. **Show real value** - time saved, quality output
5. **Be ready for questions** about the tech stack

---

**Good luck with your hackathon! You've got this! 🚀**

For urgent help during the hackathon, check:
- Logs: `docker-compose logs` or browser console
- API status: https://status.openai.com
- Quick fix: Restart the service


