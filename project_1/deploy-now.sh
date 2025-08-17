#!/bin/bash

# Quick deployment script for Google Cloud Run
# This script uses the optimized configuration that works immediately

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Quick Deploy to Google Cloud Run${NC}"
echo "===================================="

# Check if PROJECT_ID is provided as argument or environment variable
PROJECT_ID=${1:-${GCP_PROJECT_ID:-""}}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Please provide your Google Cloud Project ID${NC}"
    echo "Usage: ./deploy-now.sh YOUR_PROJECT_ID"
    echo "Or set: export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

REGION=${GCP_REGION:-"us-central1"}

echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Region: ${REGION}${NC}"
echo ""

# Set up gcloud
echo -e "${GREEN}Setting up Google Cloud configuration...${NC}"
gcloud config set project ${PROJECT_ID}
gcloud config set run/region ${REGION}

# Enable required APIs
echo -e "${GREEN}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com containerregistry.googleapis.com cloudbuild.googleapis.com --project=${PROJECT_ID}

# Use the Cloud Run optimized Dockerfile
echo -e "${GREEN}Preparing optimized configuration...${NC}"
cp Dockerfile.cloudrun Dockerfile

# Deploy using Cloud Build
echo -e "${GREEN}Starting deployment to Cloud Run...${NC}"
echo -e "${YELLOW}This will take about 3-5 minutes...${NC}"

gcloud run deploy screenshot-search \
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

# Get service URL
if [ $? -eq 0 ]; then
    SERVICE_URL=$(gcloud run services describe screenshot-search \
        --platform managed \
        --region ${REGION} \
        --project ${PROJECT_ID} \
        --format 'value(status.url)')
    
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}===================================${NC}"
    echo -e "${GREEN}Your app is now live at:${NC}"
    echo -e "${YELLOW}${SERVICE_URL}${NC}"
    echo ""
    echo -e "${GREEN}Test your app by:${NC}"
    echo "1. Opening the URL above in your browser"
    echo "2. Uploading some screenshots"
    echo "3. Searching with keywords like 'sample', 'image', or 'text'"
    echo ""
    echo -e "${YELLOW}Note: The app is in demo mode. For full AI capabilities,${NC}"
    echo -e "${YELLOW}deploy with the full version (requires more setup).${NC}"
else
    echo -e "${RED}Deployment failed. Please check the error messages above.${NC}"
    echo -e "${YELLOW}Common fixes:${NC}"
    echo "1. Make sure you're logged in: gcloud auth login"
    echo "2. Check your project ID is correct"
    echo "3. Ensure billing is enabled for your project"
    exit 1
fi

# Restore original Dockerfile
rm -f Dockerfile
echo ""
echo -e "${GREEN}Deployment complete! 🎉${NC}"

