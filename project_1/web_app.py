#!/usr/bin/env python3
"""
Flask Web Application for Screenshot Search Tool
"""

import os
import json
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from screenshot_search import ScreenshotSearcher
import uuid
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'screenshot-search-demo-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the screenshot searcher
searcher = ScreenshotSearcher(cache_file="web_cache.json")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_base64(image_path):
    """Convert image to base64 for web display."""
    try:
        with open(image_path, 'rb') as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Get image format
            img_format = image_path.split('.')[-1].lower()
            if img_format == 'jpg':
                img_format = 'jpeg'
            
            return f"data:image/{img_format};base64,{img_base64}"
    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None

@app.route('/')
def index():
    """Main page with search interface."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Handle multiple file uploads."""
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    uploaded_files = []
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add unique identifier to avoid conflicts
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            uploaded_files.append({
                'filename': unique_filename,
                'original_name': file.filename,
                'path': filepath
            })
    
    if uploaded_files:
        # Process uploaded files
        searcher.process_screenshot_folder(app.config['UPLOAD_FOLDER'])
        return jsonify({
            'success': True,
            'message': f'Uploaded and processed {len(uploaded_files)} files',
            'files': uploaded_files
        })
    else:
        return jsonify({'error': 'No valid image files uploaded'}), 400

@app.route('/api/search', methods=['POST'])
def search():
    """Handle search requests."""
    data = request.get_json()
    query = data.get('query', '').strip()
    top_k = data.get('top_k', 5)
    
    if not query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    try:
        results = searcher.search(query, top_k=top_k)
        
        # Format results for web display
        formatted_results = []
        for filename, confidence, data in results:
            # Get image as base64 for display
            image_base64 = get_image_base64(data['path'])
            
            formatted_results.append({
                'filename': filename,
                'confidence': round(confidence, 3),
                'confidence_percent': round(confidence * 100, 1),
                'path': data['path'],
                'ocr_text': data['ocr_text'],
                'visual_description': data['visual_description'],
                'ui_elements': data['ui_elements'],
                'image_data': image_base64
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results)
        })
    
    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500

@app.route('/api/status')
def status():
    """Get current status of processed screenshots."""
    total_screenshots = len(searcher.screenshots_data)
    return jsonify({
        'total_screenshots': total_screenshots,
        'cache_file': searcher.cache_file,
        'upload_folder': app.config['UPLOAD_FOLDER']
    })

@app.route('/api/clear')
def clear_data():
    """Clear all processed data and uploaded files."""
    try:
        # Clear cache
        searcher.screenshots_data = {}
        searcher._save_cache()
        
        # Remove uploaded files
        upload_folder = app.config['UPLOAD_FOLDER']
        for filename in os.listdir(upload_folder):
            if allowed_file(filename):
                os.remove(os.path.join(upload_folder, filename))
        
        return jsonify({
            'success': True,
            'message': 'All data cleared successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Failed to clear data: {str(e)}'}), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)