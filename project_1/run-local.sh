#!/bin/bash

# Local demo runner script
echo "🚀 Starting Screenshot Search App (Local Demo)"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Install dependencies if needed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip install flask==2.3.3 werkzeug==2.3.7 Pillow==10.0.0
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Start the app
echo "✅ Starting app on http://localhost:8080"
echo ""
echo "📱 Open your browser to: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop the server"
echo ""
echo "=============================================="
echo ""

# Run the app
PORT=8080 python3 app.py

