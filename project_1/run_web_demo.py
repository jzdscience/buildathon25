#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick start script for the Screenshot Search Web Demo
"""

import subprocess
import sys
import os
import webbrowser
import time

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'flask', 'werkzeug', 'pytesseract', 'PIL', 'cv2', 
        'transformers', 'torch', 'sentence_transformers', 
        'numpy', 'sklearn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'cv2':
                import cv2
            elif package == 'sklearn':
                import sklearn
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        subprocess.run(['tesseract', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("Screenshot Search Tool - Web Demo")
    print("=" * 50)
    
    # Check current directory
    if not os.path.exists('web_app.py'):
        print("Please run this script from the project directory containing web_app.py")
        return
    
    # Check Python dependencies
    print("Checking Python dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing dependencies...")
        if not install_dependencies():
            return
    else:
        print("All Python dependencies are installed!")
    
    # Check Tesseract OCR
    print("Checking Tesseract OCR...")
    if not check_tesseract():
        print("Tesseract OCR is not installed!")
        print("\nPlease install Tesseract OCR:")
        print("- macOS: brew install tesseract")
        print("- Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        
        choice = input("\nContinue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            return
    else:
        print("Tesseract OCR is installed!")
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    
    print("\nStarting web application...")
    print("The demo will open in your browser at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)
    
    # Start the Flask app
    try:
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Run the Flask app
        from web_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n\nDemo stopped. Thank you for using Screenshot Search Tool!")
    except Exception as e:
        print(f"\nError starting the web application: {e}")
        print("\nTry running manually with: python web_app.py")

if __name__ == "__main__":
    main()