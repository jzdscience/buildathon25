# 🎯 Running Screenshot Search App Locally

## Quick Start (One Command)

```bash
./run-local.sh
```

Then open: **http://localhost:8080** 🎉

## Manual Setup

### 1. Install Dependencies

```bash
# Install minimal requirements
pip install flask werkzeug Pillow

# Or use the requirements file
pip install -r requirements-simple.txt
```

### 2. Run the App

```bash
# Run with default port 8080
python app.py

# Or specify a different port
PORT=5000 python app.py
```

### 3. Access the App

Open your browser to:
- **http://localhost:8080** (default)
- **http://localhost:5000** (if you changed the port)

## 🎮 How to Use

1. **Upload Screenshots**
   - Click "Choose Files" or drag & drop images
   - Click "Process Screenshots" to upload them

2. **Search**
   - Enter keywords like "sample", "image", "text"
   - Click Search or press Enter
   - View results with confidence scores

3. **Demo Features**
   - Basic image metadata extraction
   - Simple text matching (demo mode)
   - Image preview with base64 encoding
   - Multi-file upload support

## 💻 System Requirements

- Python 3.8 or later
- 100MB free disk space
- Any modern web browser

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Kill the process using port 8080
lsof -ti:8080 | xargs kill -9

# Or use a different port
PORT=5001 python app.py
```

### Missing Dependencies
```bash
pip install flask==2.3.3 werkzeug==2.3.7 Pillow==10.0.0
```

### Permission Issues
```bash
# Make sure uploads directory is writable
chmod 777 uploads/
```

## 📁 Files Created

- `uploads/` - Stores uploaded images temporarily
- Images are stored with unique IDs to prevent conflicts

## 🔒 Security Note

This is a demo app configured for local testing:
- Runs on all interfaces (0.0.0.0)
- No authentication required
- Debug mode disabled
- 16MB max file upload size

## 🚀 Next Steps

Ready to deploy to the cloud?
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for Google Cloud Run
- Run `./deploy-now.sh` for instant cloud deployment

## 📸 Demo Mode vs Full Version

**Current (Demo Mode):**
- Simple text matching
- Basic image metadata
- Fast and lightweight
- No external dependencies

**Full Version (with AI):**
- OCR text extraction (Tesseract)
- Visual content analysis (BLIP)
- Semantic search (Sentence Transformers)
- Requires additional setup

---

**Enjoy your local demo! 🎉**

