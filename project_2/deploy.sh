#!/bin/bash

# Voice-to-Slide Generator - Google Cloud Run Deployment Script
# This script automates the deployment process to Google Cloud Run

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-""}
REGION=${GCP_REGION:-"us-central1"}
SERVICE_NAME="voice-to-slide-generator"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Function to print colored messages
print_message() {
    echo -e "${2}${1}${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
print_message "Checking prerequisites..." "$YELLOW"

if ! command_exists gcloud; then
    print_message "Error: gcloud CLI is not installed. Please install it from: https://cloud.google.com/sdk/docs/install" "$RED"
    exit 1
fi

if ! command_exists docker; then
    print_message "Error: Docker is not installed. Please install Docker first." "$RED"
    exit 1
fi

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    print_message "Please enter your Google Cloud Project ID:" "$YELLOW"
    read -r PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        print_message "Error: Project ID is required" "$RED"
        exit 1
    fi
fi

# Set the project
print_message "Setting Google Cloud project to: $PROJECT_ID" "$GREEN"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
print_message "Enabling required Google Cloud APIs..." "$YELLOW"
gcloud services enable cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com

# Check if OpenAI API key secret exists, if not create it
print_message "Checking for OpenAI API key secret..." "$YELLOW"
if ! gcloud secrets describe openai-api-key --project="$PROJECT_ID" >/dev/null 2>&1; then
    print_message "OpenAI API key secret not found. Please enter your OpenAI API key:" "$YELLOW"
    read -rs OPENAI_KEY
    echo
    if [ -z "$OPENAI_KEY" ]; then
        print_message "Warning: OpenAI API key not provided. You'll need to set it manually later." "$YELLOW"
    else
        echo -n "$OPENAI_KEY" | gcloud secrets create openai-api-key \
            --data-file=- \
            --replication-policy="automatic"
        print_message "OpenAI API key secret created successfully" "$GREEN"
    fi
else
    print_message "OpenAI API key secret already exists" "$GREEN"
fi

# Grant Cloud Run access to the secret
print_message "Granting Cloud Run access to secrets..." "$YELLOW"
gcloud secrets add-iam-policy-binding openai-api-key \
    --member="serviceAccount:${PROJECT_ID}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" >/dev/null 2>&1 || true

# Build options
print_message "Choose deployment method:" "$YELLOW"
echo "1. Use Cloud Build (recommended)"
echo "2. Build locally and push"
read -r BUILD_OPTION

if [ "$BUILD_OPTION" = "1" ]; then
    # Use Cloud Build
    print_message "Submitting build to Cloud Build..." "$YELLOW"
    gcloud builds submit --config=cloudbuild.yaml \
        --substitutions=_REGION="$REGION" \
        --timeout=20m
    print_message "Build and deployment completed via Cloud Build!" "$GREEN"
else
    # Build locally
    print_message "Building Docker image locally..." "$YELLOW"
    docker build -t "$IMAGE_NAME:latest" .
    
    # Configure Docker for GCR
    print_message "Configuring Docker for Google Container Registry..." "$YELLOW"
    gcloud auth configure-docker
    
    # Push the image
    print_message "Pushing image to Container Registry..." "$YELLOW"
    docker push "$IMAGE_NAME:latest"
    
    # Deploy to Cloud Run
    print_message "Deploying to Cloud Run..." "$YELLOW"
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE_NAME:latest" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 300 \
        --max-instances 10 \
        --min-instances 0 \
        --set-env-vars NODE_ENV=production \
        --update-secrets OPENAI_API_KEY=openai-api-key:latest
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --platform managed \
    --region "$REGION" \
    --format 'value(status.url)')

print_message "\n✅ Deployment successful!" "$GREEN"
print_message "Your Voice-to-Slide Generator is now available at:" "$GREEN"
print_message "$SERVICE_URL" "$YELLOW"
print_message "\nTo update the OpenAI API key later, run:" "$NC"
print_message "echo -n 'your-new-key' | gcloud secrets versions add openai-api-key --data-file=-" "$NC"
print_message "\nTo view logs:" "$NC"
print_message "gcloud run services logs read $SERVICE_NAME --region=$REGION" "$NC"


