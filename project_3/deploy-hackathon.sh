#!/bin/bash

# Employee Engagement Pulse - Hackathon Demo Deployment
set -e

echo "🚀 Deploying Employee Engagement Pulse to Google Cloud Run..."
echo ""
echo "⚠️  Demo Mode: Environment variables are baked into the image"
echo "   (Not recommended for production!)"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your Slack tokens."
    exit 1
fi

# Copy .env to .env.docker (to avoid .gitignore issues)
echo "📋 Copying .env to .env.docker for Docker build..."
cp .env .env.docker

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No Google Cloud project set. Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Building and pushing Docker image..."
echo "   Project: $PROJECT_ID"
echo ""

# Build and push image
gcloud builds submit --tag gcr.io/$PROJECT_ID/employee-engagement-pulse

echo ""
echo "🌐 Deploying to Cloud Run..."

# Deploy to Cloud Run
gcloud run deploy employee-engagement-pulse \
    --image gcr.io/$PROJECT_ID/employee-engagement-pulse \
    --port 8000 \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 1Gi \
    --min-instances 0 \
    --max-instances 10

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🎯 Your app is now running at:"
gcloud run services describe employee-engagement-pulse \
    --platform managed \
    --region us-central1 \
    --format 'value(status.url)'

echo ""
echo "📊 Access your dashboard:"
echo "   Frontend: [URL above]"
echo "   API Docs: [URL above]/docs"
echo "   Health Check: [URL above]/health"
echo ""
echo "🎉 Ready for your hackathon demo!"
