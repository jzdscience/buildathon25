#!/bin/bash
echo "🚀 Starting Employee Engagement Pulse in production mode..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your configuration."
    exit 1
fi

# Check if frontend build exists
if [ ! -d "frontend/build" ]; then
    echo "❌ Frontend build not found. Please run ./build-production.sh first"
    exit 1
fi

cd backend
source venv/bin/activate

echo "🌐 Starting server on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
