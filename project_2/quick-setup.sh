#!/bin/bash

# Ultra-quick setup for hackathon demo
echo "🚀 Voice-to-Slide Generator - Quick Setup"
echo "========================================="
echo ""
echo "Enter your OpenAI API key:"
echo "(Get one from: https://platform.openai.com/api-keys)"
read -rs OPENAI_KEY
echo ""

if [ -z "$OPENAI_KEY" ]; then
    echo "❌ Error: API key is required!"
    exit 1
fi

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=$OPENAI_KEY
PORT=3000
NODE_ENV=production
EOF

echo "✅ .env file created!"
echo ""
echo "Now run one of these commands:"
echo ""
echo "  Local:   npm install && npm start"
echo "  Docker:  docker-compose up"
echo "  Cloud:   ./deploy.sh"
echo ""
echo "Your app will be available at:"
echo "  Local:   http://localhost:3000"
echo "  Docker:  http://localhost:8080"
echo ""


