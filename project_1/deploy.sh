#!/bin/bash

# Google Cloud Run Deployment Script
# This script helps deploy the Screenshot Search app to Google Cloud Run

set -e

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-""}
SERVICE_NAME="screenshot-search"
REGION=${GCP_REGION:-"us-central1"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_message() {
    echo -e "${2}${1}${NC}"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_message "Error: gcloud CLI is not installed. Please install it first." "$RED"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    print_message "Error: GCP_PROJECT_ID environment variable is not set." "$RED"
    echo "Please run: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

# Function to deploy using Cloud Build
deploy_with_cloud_build() {
    print_message "Deploying with Cloud Build..." "$GREEN"
    gcloud builds submit --config cloudbuild.yaml \
        --substitutions=_REGION=${REGION} \
        --project=${PROJECT_ID}
}

# Function to deploy using local Docker build
deploy_with_local_build() {
    print_message "Building Docker image locally..." "$GREEN"
    
    # Choose Dockerfile based on deployment type
    if [ "$1" == "simple" ]; then
        docker build -f Dockerfile.simple -t ${IMAGE_NAME}:latest .
        print_message "Using simplified version (no AI dependencies)" "$YELLOW"
    else
        docker build -f Dockerfile -t ${IMAGE_NAME}:latest .
        print_message "Using full version with AI capabilities" "$YELLOW"
    fi
    
    print_message "Pushing image to Google Container Registry..." "$GREEN"
    docker push ${IMAGE_NAME}:latest
    
    print_message "Deploying to Cloud Run..." "$GREEN"
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
        --project ${PROJECT_ID}
}

# Function to deploy directly using source code
deploy_from_source() {
    print_message "Deploying directly from source..." "$GREEN"
    
    # Use the Cloud Run optimized Dockerfile for deployment
    cp Dockerfile.cloudrun Dockerfile
    
    gcloud run deploy ${SERVICE_NAME} \
        --source . \
        --platform managed \
        --region ${REGION} \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --max-instances 10 \
        --min-instances 0 \
        --port 8080 \
        --project ${PROJECT_ID}
    
    # Restore original Dockerfile
    git checkout Dockerfile 2>/dev/null || true
}

# Main menu
echo "================================"
echo "Screenshot Search App Deployment"
echo "================================"
echo ""
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service Name: ${SERVICE_NAME}"
echo ""
echo "Select deployment method:"
echo "1) Deploy with Cloud Build (recommended)"
echo "2) Deploy with local Docker build (full version)"
echo "3) Deploy with local Docker build (simple version)"
echo "4) Deploy directly from source (simple version)"
echo "5) Setup project (configure gcloud)"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        deploy_with_cloud_build
        ;;
    2)
        deploy_with_local_build "full"
        ;;
    3)
        deploy_with_local_build "simple"
        ;;
    4)
        deploy_from_source
        ;;
    5)
        print_message "Setting up gcloud configuration..." "$GREEN"
        gcloud config set project ${PROJECT_ID}
        gcloud config set run/region ${REGION}
        gcloud auth configure-docker
        print_message "Setup complete!" "$GREEN"
        ;;
    6)
        print_message "Exiting..." "$YELLOW"
        exit 0
        ;;
    *)
        print_message "Invalid choice!" "$RED"
        exit 1
        ;;
esac

# Get the service URL
if [ $? -eq 0 ] && [ $choice -ne 5 ] && [ $choice -ne 6 ]; then
    SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
        --platform managed \
        --region ${REGION} \
        --project ${PROJECT_ID} \
        --format 'value(status.url)')
    
    print_message "\n✅ Deployment successful!" "$GREEN"
    print_message "Service URL: ${SERVICE_URL}" "$GREEN"
    print_message "\nYou can now access your Screenshot Search app at the URL above." "$YELLOW"
fi
