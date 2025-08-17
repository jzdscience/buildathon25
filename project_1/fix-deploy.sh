#!/bin/bash

# Quick fix deployment script - uses the simplest configuration that works
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔧 Cloud Run Deployment Fix${NC}"
echo "================================"

PROJECT_ID=${1:-${GCP_PROJECT_ID:-""}}

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Please provide your Google Cloud Project ID${NC}"
    echo "Usage: ./fix-deploy.sh YOUR_PROJECT_ID"
    exit 1
fi

REGION=${GCP_REGION:-"us-central1"}

echo -e "${YELLOW}Using simplified Flask configuration for deployment...${NC}"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# Use the simple Flask Dockerfile that definitely works
echo -e "${GREEN}Preparing simplified deployment...${NC}"
cp Dockerfile.simple-flask Dockerfile

# Deploy with explicit timeout and memory settings
echo -e "${GREEN}Deploying to Cloud Run...${NC}"
gcloud run deploy screenshot-search \
    --source . \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --timeout 60 \
    --max-instances 5 \
    --min-instances 0 \
    --port 8080 \
    --project ${PROJECT_ID} \
    --set-env-vars "PYTHONUNBUFFERED=1"

# Check deployment status
if [ $? -eq 0 ]; then
    SERVICE_URL=$(gcloud run services describe screenshot-search \
        --platform managed \
        --region ${REGION} \
        --project ${PROJECT_ID} \
        --format 'value(status.url)')
    
    echo ""
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}Your app is now live at:${NC}"
    echo -e "${YELLOW}${SERVICE_URL}${NC}"
    echo ""
    echo -e "${GREEN}The app is running in simple Flask mode (no gunicorn).${NC}"
    echo -e "${YELLOW}This is fine for demo/testing purposes.${NC}"
else
    echo -e "${RED}Deployment failed. Checking logs...${NC}"
    echo ""
    echo "Recent logs:"
    gcloud run services logs read screenshot-search --limit=20 --project=${PROJECT_ID}
    echo ""
    echo -e "${YELLOW}Troubleshooting tips:${NC}"
    echo "1. Make sure billing is enabled for your project"
    echo "2. Check that all APIs are enabled:"
    echo "   gcloud services enable run.googleapis.com cloudbuild.googleapis.com"
    echo "3. Try running: gcloud auth login"
fi

# Clean up
rm -f Dockerfile

