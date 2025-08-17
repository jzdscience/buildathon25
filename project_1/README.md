# Screenshot Search Tool

Search your screenshot history using natural language queries for both text content AND visual elements.

## Features

- **OCR Text Extraction**: Extracts readable text from screenshots using Tesseract
- **Visual Description**: Generates descriptions of visual content using BLIP model
- **UI Element Detection**: Identifies buttons, color schemes, and interface elements
- **Semantic Search**: Uses sentence transformers for intelligent query matching
- **Confidence Scoring**: Returns top 5 matches with similarity scores
- **Caching**: Processes screenshots once and caches results for fast searches

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- **macOS**: `brew install tesseract`
- **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`
- **Windows**: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

## Usage

### Process Screenshots
```bash
python screenshot_search.py --folder /path/to/screenshots
```

### Search with Query
```bash
python screenshot_search.py --query "error message about auth"
python screenshot_search.py --query "screenshot with blue button"
```

### Interactive Mode
```bash
python screenshot_search.py
```

### Full Example
```bash
# Process folder and search
python screenshot_search.py --folder ./screenshots --query "login screen" --top 3
```

## Command Line Options

- `--folder, -f`: Folder containing screenshots to process
- `--query, -q`: Search query (text or visual description)
- `--top, -t`: Number of top results (default: 5)
- `--cache, -c`: Cache file path (default: screenshot_cache.json)

## Example Queries

### Text-based searches:
- "error message"
- "login failed"
- "save button"
- "email address"

### Visual-based searches:
- "screenshot with blue button"
- "red error dialog"
- "settings screen"
- "dark theme interface"

### Combined searches:
- "blue submit button with text"
- "error message in red popup"
- "dashboard with charts"

## How It Works

1. **Text Extraction**: Uses Tesseract OCR to extract all readable text
2. **Visual Analysis**: BLIP model generates natural language descriptions
3. **UI Detection**: OpenCV detects interface elements and color schemes
4. **Embedding**: Combines all features into semantic embeddings
5. **Search**: Cosine similarity matching against query embeddings
6. **Ranking**: Returns top matches with confidence scores

## Performance Notes

- First run processes all screenshots (slow)
- Subsequent searches are fast using cached embeddings
- Only reprocesses changed files
- Supports common image formats: PNG, JPG, JPEG, BMP, TIFF, WebP