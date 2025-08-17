#!/bin/bash

# Employee Engagement Pulse - Setup Verification Script
set -e

echo "🔍 Verifying Employee Engagement Pulse setup..."
echo ""

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found"
    ERRORS=1
fi

# Check if Node.js is available
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js: $NODE_VERSION"
else
    echo "❌ Node.js not found"
    ERRORS=1
fi

# Check if npm is available
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm: $NPM_VERSION"
else
    echo "❌ npm not found"
    ERRORS=1
fi

echo ""

# Check if backend is set up
if [ -d "backend/venv" ]; then
    echo "✅ Backend virtual environment exists"
else
    echo "⚠️  Backend virtual environment not found - run ./setup-dev.sh"
    WARNINGS=1
fi

# Check if frontend is set up
if [ -d "frontend/node_modules" ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "⚠️  Frontend dependencies not installed - run ./setup-dev.sh"
    WARNINGS=1
fi

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ Environment file (.env) exists"
    
    # Check if Slack tokens are configured
    if grep -q "xoxb-" .env && grep -q "xapp-" .env; then
        echo "✅ Slack tokens appear to be configured"
    else
        echo "⚠️  Slack tokens may not be configured in .env"
        WARNINGS=1
    fi
else
    echo "⚠️  Environment file (.env) not found"
    WARNINGS=1
fi

# Check if data directory exists
if [ -d "data" ]; then
    echo "✅ Data directory exists"
else
    echo "⚠️  Data directory not found - will be created automatically"
fi

echo ""

# Summary
if [ "$ERRORS" = "1" ]; then
    echo "❌ Setup verification failed. Please install missing dependencies."
    echo "   See README.md for installation instructions."
    exit 1
elif [ "$WARNINGS" = "1" ]; then
    echo "⚠️  Setup partially complete. Recommendations:"
    echo "   1. Run ./setup-dev.sh if you haven't already"
    echo "   2. Configure Slack tokens in .env file"
    echo "   3. Run ./start-dev.sh to start the application"
else
    echo "🎉 Everything looks good! Your setup is ready."
    echo ""
    echo "🚀 To start the application:"
    echo "   ./start-dev.sh"
    echo ""
    echo "🌐 The application will be available at:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend: http://localhost:8000"
fi

echo ""
echo "📖 For detailed instructions, see README.md"

