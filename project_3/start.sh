#!/bin/bash

# Employee Engagement Pulse - Quick Start Script
set -e

echo "🚀 Starting Employee Engagement Pulse..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

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
        read -p "Press Enter when you've configured your .env file..." -n1 -s
        echo ""
    else
        echo "❌ Template file not found. Please create .env manually."
        exit 1
    fi
fi

# Create data directory
mkdir -p data
echo "📁 Created data directory for database"

# Build and start the application
echo "🏗️  Building Docker containers..."
docker-compose build

echo "🚀 Starting the application..."
docker-compose up -d

# Wait for the application to be ready
echo "⏳ Waiting for application to be ready..."
sleep 10

# Check if the application is running
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo ""
    echo "✅ Employee Engagement Pulse is running!"
    echo ""
    echo "🌐 Dashboard: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo "📊 Health Check: http://localhost:8000/health"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Open http://localhost:8000 in your browser"
    echo "   2. Go to Settings → Test Slack connection"
    echo "   3. Go to Channels → Add your Slack channels"
    echo "   4. Go to Settings → Start monitoring"
    echo "   5. View your team's sentiment on the Dashboard"
    echo ""
    echo "📖 For detailed setup instructions, see README.md"
    echo ""
    echo "🛑 To stop: docker-compose down"
    echo "📝 To view logs: docker-compose logs -f"
else
    echo ""
    echo "❌ Application failed to start properly."
    echo "🔍 Check logs with: docker-compose logs"
    echo ""
    docker-compose logs --tail=20
fi

