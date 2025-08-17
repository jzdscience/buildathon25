#!/bin/bash

# Quick redeploy script for Google Cloud Run
# Use this after making fixes to redeploy your service

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 Voice-to-Slide Generator - Quick Redeploy${NC}"
echo -e "${YELLOW}This will rebuild and redeploy your service with the latest fixes${NC}\n"

# Check if PROJECT_ID is set
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
    read -r GCP_PROJECT_ID
fi

REGION=${GCP_REGION:-"us-central1"}

echo -e "${GREEN}Using Project: $GCP_PROJECT_ID${NC}"
echo -e "${GREEN}Using Region: $REGION${NC}\n"

# Set the project
gcloud config set project "$GCP_PROJECT_ID"

# Submit to Cloud Build with the fixed Dockerfile
echo -e "${YELLOW}Submitting to Cloud Build...${NC}"
gcloud builds submit \
    --config=cloudbuild.yaml \
    --substitutions=_REGION="$REGION" \
    --timeout=20m

# Get the service URL
SERVICE_URL=$(gcloud run services describe voice-to-slide-generator \
    --platform managed \
    --region "$REGION" \
    --format 'value(status.url)')

echo -e "\n${GREEN}✅ Redeployment successful!${NC}"
echo -e "${GREEN}Your service is available at:${NC}"
echo -e "${YELLOW}$SERVICE_URL${NC}\n"

echo -e "To check logs for any issues:"
echo -e "gcloud run services logs read voice-to-slide-generator --region=$REGION --limit=50"


