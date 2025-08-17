#!/bin/bash

# Google Cloud Run Deployment Script
# This script helps deploy the Knowledge Graph Builder to Google Cloud Run

set -e

# Configuration
PROJECT_ID=""
REGION="us-central1"
SERVICE_NAME="knowledge-graph-builder"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first:"
    echo "https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get or set project ID
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    if [ -z "$PROJECT_ID" ]; then
        print_error "No Google Cloud project is set. Please set a project:"
        echo "gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
fi

print_status "Using Google Cloud Project: $PROJECT_ID"

# Update image name with project ID
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Check if user wants to use Cloud Build or local build
echo ""
echo "Choose deployment method:"
echo "1. Use Google Cloud Build (recommended)"
echo "2. Build locally and push to Container Registry"
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        print_status "Using Google Cloud Build..."
        
        # Submit build to Cloud Build
        gcloud builds submit --config cloudbuild.yaml \
            --substitutions=COMMIT_SHA=latest \
            --project=$PROJECT_ID
        
        print_status "Build and deployment completed via Cloud Build!"
        ;;
    2)
        print_status "Building Docker image locally..."
        
        # Build the Docker image
        docker build -t ${IMAGE_NAME}:latest .
        
        print_status "Docker image built successfully!"
        
        # Configure Docker to use gcloud as credential helper
        gcloud auth configure-docker
        
        print_status "Pushing image to Google Container Registry..."
        
        # Push the image to GCR
        docker push ${IMAGE_NAME}:latest
        
        print_status "Image pushed successfully!"
        
        print_status "Deploying to Cloud Run..."
        
        # Deploy to Cloud Run
        gcloud run deploy ${SERVICE_NAME} \
            --image ${IMAGE_NAME}:latest \
            --platform managed \
            --region ${REGION} \
            --allow-unauthenticated \
            --memory 2Gi \
            --cpu 2 \
            --timeout 300 \
            --max-instances 10 \
            --min-instances 0 \
            --port 8080 \
            --project $PROJECT_ID
        
        print_status "Deployment completed!"
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Get the service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
    --platform managed \
    --region ${REGION} \
    --format 'value(status.url)' \
    --project $PROJECT_ID)

if [ ! -z "$SERVICE_URL" ]; then
    echo ""
    print_status "Your application is deployed and available at:"
    echo -e "${GREEN}${SERVICE_URL}${NC}"
    echo ""
    echo "You can test it by visiting the URL in your browser."
else
    print_warning "Could not retrieve service URL. Check the deployment status with:"
    echo "gcloud run services list --project $PROJECT_ID"
fi

echo ""
print_status "Deployment script completed!"
echo ""
echo "Useful commands:"
echo "- View logs: gcloud run services logs read ${SERVICE_NAME} --project $PROJECT_ID"
echo "- Update service: gcloud run services update ${SERVICE_NAME} --project $PROJECT_ID"
echo "- Delete service: gcloud run services delete ${SERVICE_NAME} --project $PROJECT_ID"

