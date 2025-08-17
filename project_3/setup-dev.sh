#!/bin/bash

# Employee Engagement Pulse - Local Development Setup
set -e

echo "🛠️  Setting up Employee Engagement Pulse for local development..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first:"
    echo "   https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Found Python $PYTHON_VERSION"

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first:"
    echo "   https://nodejs.org/en/download/"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "✅ Found Node.js $NODE_VERSION"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    if [ -f backend/env.template ]; then
        cp backend/env.template .env
        echo "✅ Created .env file from template"
        echo ""
        echo "🔧 IMPORTANT: Please edit .env file with your Slack credentials:"
        echo "   - SLACK_BOT_TOKEN=xoxb-your-bot-token"
        echo "   - SLACK_APP_TOKEN=xapp-your-app-token"
        echo "   - SECRET_KEY=your-secure-secret-key"
        echo ""
        echo "📖 See README.md for detailed Slack app setup instructions."
        echo ""
    else
        echo "❌ Template file not found. Please create .env manually."
        exit 1
    fi
fi

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

cd ..

# Setup frontend
echo "⚛️  Setting up React frontend..."
cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

cd ..

# Create data directory
mkdir -p data
echo "📁 Created data directory for database"

# Create startup scripts
echo "📝 Creating startup scripts..."

# Backend startup script
cat > start-backend.sh << 'EOF'
#!/bin/bash
echo "🐍 Starting FastAPI backend..."
cd backend
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
EOF

# Frontend startup script
cat > start-frontend.sh << 'EOF'
#!/bin/bash
echo "⚛️  Starting React frontend..."
cd frontend
npm start
EOF

# Combined startup script
cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Employee Engagement Pulse in development mode..."
echo ""
echo "Starting backend on http://localhost:8000"
echo "Starting frontend on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $(jobs -p) 2>/dev/null || true
    wait
    echo "✅ Services stopped"
}

trap cleanup EXIT INT TERM

# Start backend in background
cd backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
cd ../frontend && npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

# Make scripts executable
chmod +x start-backend.sh
chmod +x start-frontend.sh
chmod +x start-dev.sh

echo ""
echo "✅ Local development setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   ./start-dev.sh          # Start both backend and frontend"
echo "   ./start-backend.sh      # Start only backend (port 8000)"
echo "   ./start-frontend.sh     # Start only frontend (port 3000)"
echo ""
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔧 Next steps:"
echo "   1. Edit .env file with your Slack credentials"
echo "   2. Run ./start-dev.sh to start the application"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "📖 For detailed setup instructions, see README.md"

