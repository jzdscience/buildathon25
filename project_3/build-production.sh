#!/bin/bash

# Employee Engagement Pulse - Production Build Script
set -e

echo "🏗️  Building Employee Engagement Pulse for production..."
echo ""

# Check if setup has been run
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend not set up. Please run ./setup-dev.sh first"
    exit 1
fi

if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend not set up. Please run ./setup-dev.sh first"
    exit 1
fi

# Build frontend
echo "⚛️  Building React frontend for production..."
cd frontend
npm run build
cd ..

echo "✅ Frontend build complete!"
echo ""

# Check if backend virtual environment exists
if [ ! -f "backend/venv/bin/activate" ]; then
    echo "❌ Backend virtual environment not found. Please run ./setup-dev.sh first"
    exit 1
fi

# Create production startup script
cat > start-production.sh << 'EOF'
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
EOF

chmod +x start-production.sh

echo "✅ Production build complete!"
echo ""
echo "🚀 To start in production mode:"
echo "   ./start-production.sh"
echo ""
echo "🌐 The application will be available at:"
echo "   http://localhost:8000 (Frontend + API)"
echo "   http://localhost:8000/docs (API Documentation)"
echo ""
echo "📝 Note: In production mode, the backend serves the built frontend"
echo "     No need to run the frontend development server separately"
