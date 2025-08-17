# Screenshot Search Tool - Web Demo

A beautiful, interactive web interface for searching screenshots using natural language queries.

## ✨ Features

- **🖱️ Drag & Drop Upload**: Simply drag screenshot files into the browser
- **🔍 Smart Search**: Natural language queries for both text and visual content
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🖼️ Image Previews**: See thumbnails of matching screenshots
- **📊 Confidence Scores**: Visual indicators of match quality
- **⚡ Real-time Results**: Instant search with confidence scoring

## 🚀 Quick Start

### Option 1: Auto-Setup (Recommended)
```bash
python run_web_demo.py
```
This script will:
- Check and install all dependencies
- Verify Tesseract OCR installation
- Start the web server
- Open your browser automatically

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (if not already installed)
# macOS: brew install tesseract
# Ubuntu: sudo apt-get install tesseract-ocr

# Start the web server
python web_app.py
```

Then open your browser to: http://localhost:5000

## 🎯 How to Use

### 1. Upload Screenshots
- **Drag & Drop**: Drag image files directly into the upload area
- **File Browser**: Click "Choose Files" to select screenshots
- **Batch Processing**: Upload multiple files at once

### 2. Search Your Screenshots
Try these example queries:
- **Text-based**: "error message", "login screen", "password field"
- **Visual-based**: "blue button", "red error dialog", "dark theme"
- **Combined**: "error message with red text", "login screen with blue button"

### 3. View Results
- **Image Previews**: See thumbnails of matching screenshots
- **Confidence Scores**: Percentage match indicators
- **Text Content**: OCR-extracted text from screenshots
- **Visual Descriptions**: AI-generated descriptions of visual content
- **UI Elements**: Detected interface components and colors

## 🖥️ Web Interface Features

### Upload Section
- Modern drag-and-drop interface
- Support for PNG, JPG, JPEG, BMP, TIFF, WebP
- Real-time upload progress
- Batch file processing

### Search Interface
- Clean, intuitive search box
- Pre-defined example queries for quick testing
- Real-time search with loading indicators
- Keyboard shortcuts (Enter to search)

### Results Display
- Card-based layout with image previews
- Confidence score visualization
- Expandable content details
- Responsive grid for different screen sizes

### Status Management
- Live count of processed screenshots
- Clear data functionality
- Error handling and user feedback
- Processing status indicators

## 🎨 Design Features

- **Modern UI**: Clean, gradient-based design
- **Responsive Layout**: Adapts to all screen sizes
- **Smooth Animations**: Hover effects and transitions
- **Loading States**: Visual feedback during operations
- **Error Handling**: User-friendly error messages

## 🔧 Technical Details

### Backend (Flask)
- RESTful API endpoints
- File upload handling
- Image processing pipeline
- Semantic search engine

### Frontend (HTML/CSS/JavaScript)
- Vanilla JavaScript (no frameworks required)
- CSS Grid and Flexbox layouts
- Drag-and-drop file handling
- AJAX API communication

### API Endpoints
- `POST /api/upload` - Upload and process screenshots
- `POST /api/search` - Perform natural language search
- `GET /api/status` - Get processing status
- `GET /api/clear` - Clear all data

## 🔍 Search Examples

### Text Content Searches
```
"login failed"          → Find screenshots with login error messages
"save button"           → Find screenshots containing save buttons
"email address"         → Find screenshots with email input fields
"404 error"             → Find screenshots showing 404 pages
```

### Visual Content Searches
```
"blue interface"        → Find screenshots with blue color schemes
"dark theme"            → Find screenshots with dark backgrounds
"red error message"     → Find screenshots with red error dialogs
"settings screen"       → Find screenshots of settings pages
```

### Combined Searches
```
"blue submit button"    → Find blue-colored submit buttons
"error in red popup"    → Find error messages in red dialog boxes
"login with password"   → Find login screens with password fields
"dark settings page"    → Find settings pages with dark themes
```

## 🛠️ Dependencies

### Python Packages
- `flask` - Web framework
- `pytesseract` - OCR text extraction
- `transformers` - AI image descriptions
- `sentence-transformers` - Semantic search
- `opencv-python` - Image processing
- `Pillow` - Image handling

### System Requirements
- **Tesseract OCR** - Required for text extraction
- **Python 3.8+** - Modern Python version
- **4GB+ RAM** - For AI model loading

## 📱 Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 🔒 Privacy & Security

- All processing happens locally on your machine
- No data is sent to external servers
- Screenshots are stored temporarily in local uploads folder
- Clear data function removes all processed information

## 🚨 Troubleshooting

### Common Issues

**"Tesseract not found"**
```bash
# Install Tesseract OCR
brew install tesseract  # macOS
sudo apt-get install tesseract-ocr  # Ubuntu
```

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"Permission denied"**
```bash
# Make sure uploads directory is writable
chmod 755 uploads
```

### Performance Tips

- **First Run**: Initial model loading takes 1-2 minutes
- **Large Files**: Compress screenshots for faster processing
- **Memory**: Close other applications if processing many files
- **Storage**: Clear data periodically to free up space

## 📊 Demo Flow

1. **Start**: Run `python run_web_demo.py`
2. **Upload**: Drag 5-10 sample screenshots into the interface
3. **Process**: Wait for AI processing to complete
4. **Search**: Try example queries to see results
5. **Explore**: Test different search terms and view confidence scores
6. **Clear**: Use clear data to reset and try new screenshots