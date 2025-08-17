#!/bin/bash

echo "🐳 Testing Docker build locally..."
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t employee-engagement-pulse-test . || {
    echo "❌ Docker build failed"
    exit 1
}

echo ""
echo "✅ Docker build successful!"
echo ""
echo "🚀 To test locally, run:"
echo "   docker run -p 8000:8000 \\"
echo "     -e SLACK_BOT_TOKEN=your-token \\"
echo "     -e SLACK_APP_TOKEN=your-app-token \\"
echo "     -e SECRET_KEY=test-secret-key \\"
echo "     employee-engagement-pulse-test"
echo ""
echo "Then visit: http://localhost:8000"
echo "The frontend should load, not just the API!"

