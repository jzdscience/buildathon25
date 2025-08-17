#!/usr/bin/env python3
"""
Startup script for Codebase Time Machine Web Interface
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    # Map package names to their import names
    package_imports = {
        'flask': 'flask',
        'flask_socketio': 'flask_socketio', 
        'gitpython': 'git',  # gitpython imports as 'git'
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'plotly': 'plotly',
        'nltk': 'nltk',
        'rich': 'rich'
    }
    
    missing_packages = []
    
    for package_name, import_name in package_imports.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nPlease run: pip install -r requirements.txt")
        return False
    
    return True

def check_nltk_data():
    """Check if NLTK data is available"""
    try:
        import nltk
        from nltk.corpus import stopwords
        stopwords.words('english')
        return True
    except:
        print("⚠️  NLTK data not found. Downloading...")
        try:
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            return True
        except:
            print("❌ Failed to download NLTK data. Some features may not work.")
            return False

def main():
    print("🚀 Starting Codebase Time Machine Web Interface...")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("❌ app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("✅ All dependencies found")
    
    # Check NLTK data
    print("🔍 Checking NLTK data...")
    check_nltk_data()
    
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    os.makedirs('repos', exist_ok=True)
    
    print("✅ Setup complete")
    print("=" * 60)
    print("🌐 Starting web server...")
    print("📍 Open your browser to: http://localhost:5000")
    print("=" * 60)
    print("💡 Features available:")
    print("   • Analyze any Git repository")
    print("   • Interactive visualizations")
    print("   • Natural language queries")
    print("   • Real-time progress updates")
    print("   • Comprehensive reports")
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the server")
    print("")
    
    # Start the Flask application
    try:
        from app import app, socketio
        # Try different ports if 5000 is in use
        for port in [5000, 5001, 5002, 8080, 8000]:
            try:
                print(f"🔌 Trying port {port}...")
                socketio.run(app, debug=False, host='0.0.0.0', port=port)
                break
            except OSError as e:
                if "Address already in use" in str(e):
                    print(f"   Port {port} is in use, trying next...")
                    continue
                else:
                    raise e
        else:
            print("❌ All ports are in use. Try stopping other applications or run: python3 app.py")
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("Try running: python3 app.py")

if __name__ == "__main__":
    main()