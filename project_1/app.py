#!/usr/bin/env python3
"""
Main application entry point for Google Cloud Run deployment
"""

import os
import json
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import uuid
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'screenshot-search-demo-key')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Simple in-memory storage for demo
screenshots_data = {}

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

def simple_text_search(query, text):
    """Simple text matching for demo purposes."""
    if not text:
        return 0.0
    
    query_words = query.lower().split()
    text_lower = text.lower()
    
    matches = sum(1 for word in query_words if word in text_lower)
    return matches / len(query_words) if query_words else 0.0

def process_image_basic(image_path, filename):
    """Basic image processing without AI dependencies."""
    try:
        # Get image info
        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format
        
        # Create mock data for demo
        mock_data = {
            'path': image_path,
            'ocr_text': f"Sample text content from {filename}. This would normally be extracted using OCR.",
            'visual_description': f"A {format_name} image with dimensions {width}x{height} pixels.",
            'ui_elements': [f"{format_name} format", f"{width}x{height} resolution"],
            'combined_text': f"Sample text from {filename} {format_name} image {width}x{height}",
            'mtime': os.path.getmtime(image_path)
        }
        
        return mock_data
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

@app.route('/')
def index():
    """Main page with search interface."""
    return render_template('simple_demo.html')

@app.route('/health')
def health():
    """Health check endpoint for Cloud Run."""
    return jsonify({'status': 'healthy'}), 200

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
            
            # Process the image
            image_data = process_image_basic(filepath, unique_filename)
            if image_data:
                screenshots_data[unique_filename] = image_data
                uploaded_files.append({
                    'filename': unique_filename,
                    'original_name': file.filename,
                    'path': filepath
                })
    
    if uploaded_files:
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
        results = []
        
        for filename, data in screenshots_data.items():
            # Simple text matching simulation
            text_score = simple_text_search(query, data['combined_text'])
            
            # Add some variation for demo
            import random
            confidence = max(0.1, text_score + random.uniform(-0.2, 0.3))
            confidence = min(1.0, confidence)
            
            results.append((filename, confidence, data))
        
        # Sort by confidence and return top k
        results.sort(key=lambda x: x[1], reverse=True)
        results = results[:top_k]
        
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
    total_screenshots = len(screenshots_data)
    return jsonify({
        'total_screenshots': total_screenshots,
        'upload_folder': app.config['UPLOAD_FOLDER']
    })

@app.route('/api/clear')
def clear_data():
    """Clear all processed data and uploaded files."""
    try:
        # Clear data
        global screenshots_data
        screenshots_data = {}
        
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

if __name__ == '__main__':
    # Use PORT environment variable if available (for Cloud Run)
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)

