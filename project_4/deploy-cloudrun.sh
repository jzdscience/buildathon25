#!/bin/bash

# Google Cloud Run Deployment Script for Codebase Time Machine

echo "================================================"
echo "Codebase Time Machine - Cloud Run Deployment"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SERVICE_NAME="codebase-time-machine"
REGION="us-central1"
MEMORY="2Gi"
CPU="2"
MAX_INSTANCES="10"
MIN_INSTANCES="0"
ALLOW_UNAUTHENTICATED="true"

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --project) PROJECT_ID="$2"; shift ;;
        --service) SERVICE_NAME="$2"; shift ;;
        --region) REGION="$2"; shift ;;
        --memory) MEMORY="$2"; shift ;;
        --cpu) CPU="$2"; shift ;;
        --max-instances) MAX_INSTANCES="$2"; shift ;;
        --min-instances) MIN_INSTANCES="$2"; shift ;;
        --no-auth) ALLOW_UNAUTHENTICATED="false" ;;
        --build-only) BUILD_ONLY="true" ;;
        --deploy-only) DEPLOY_ONLY="true" ;;
        --help) 
            echo "Usage: ./deploy-cloudrun.sh --project PROJECT_ID [OPTIONS]"
            echo ""
            echo "Required:"
            echo "  --project PROJECT_ID    GCP Project ID"
            echo ""
            echo "Options:"
            echo "  --service NAME          Service name (default: codebase-time-machine)"
            echo "  --region REGION         Deployment region (default: us-central1)"
            echo "  --memory SIZE           Memory allocation (default: 2Gi)"
            echo "  --cpu COUNT             CPU allocation (default: 2)"
            echo "  --max-instances N       Maximum instances (default: 10)"
            echo "  --min-instances N       Minimum instances (default: 0)"
            echo "  --no-auth               Require authentication"
            echo "  --build-only            Only build, don't deploy"
            echo "  --deploy-only           Only deploy existing image"
            echo "  --help                  Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./deploy-cloudrun.sh --project my-project-id"
            echo "  ./deploy-cloudrun.sh --project my-project-id --region europe-west1 --min-instances 1"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Check for required parameters
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: Project ID is required${NC}"
    echo "Usage: ./deploy-cloudrun.sh --project PROJECT_ID"
    echo "Run './deploy-cloudrun.sh --help' for more options"
    exit 1
fi

echo ""
echo -e "${YELLOW}Configuration:${NC}"
echo "  Project ID: ${PROJECT_ID}"
echo "  Service: ${SERVICE_NAME}"
echo "  Region: ${REGION}"
echo "  Memory: ${MEMORY}"
echo "  CPU: ${CPU}"
echo "  Max Instances: ${MAX_INSTANCES}"
echo "  Min Instances: ${MIN_INSTANCES}"
echo "  Allow Unauthenticated: ${ALLOW_UNAUTHENTICATED}"
echo ""

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}Error: gcloud CLI is not installed${NC}"
        echo "Please install the Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

# Function to set the project
set_project() {
    echo -e "${BLUE}Setting project to ${PROJECT_ID}...${NC}"
    gcloud config set project "${PROJECT_ID}"
}

# Function to enable required APIs
enable_apis() {
    echo -e "${BLUE}Enabling required APIs...${NC}"
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable containerregistry.googleapis.com
    echo -e "${GREEN}✓ APIs enabled${NC}"
}

# Function to build using Cloud Build
build_image() {
    echo -e "${BLUE}Building image using Cloud Build...${NC}"
    
    if [ -f "cloudbuild.yaml" ]; then
        echo "Using cloudbuild.yaml configuration..."
        if gcloud builds submit --config cloudbuild.yaml; then
            echo -e "${GREEN}✓ Image built successfully${NC}"
        else
            echo -e "${RED}✗ Build failed${NC}"
            exit 1
        fi
    else
        echo "Building directly..."
        IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
        if gcloud builds submit --tag "${IMAGE_NAME}"; then
            echo -e "${GREEN}✓ Image built successfully${NC}"
        else
            echo -e "${RED}✗ Build failed${NC}"
            exit 1
        fi
    fi
}

# Function to deploy to Cloud Run
deploy_service() {
    echo -e "${BLUE}Deploying to Cloud Run...${NC}"
    
    IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
    
    # Build deployment command
    DEPLOY_CMD="gcloud run deploy ${SERVICE_NAME} \
        --image ${IMAGE_NAME} \
        --platform managed \
        --region ${REGION} \
        --memory ${MEMORY} \
        --cpu ${CPU} \
        --timeout 900 \
        --max-instances ${MAX_INSTANCES} \
        --min-instances ${MIN_INSTANCES} \
        --port 8080 \
        --set-env-vars PYTHONUNBUFFERED=1"
    
    if [ "${ALLOW_UNAUTHENTICATED}" = "true" ]; then
        DEPLOY_CMD="${DEPLOY_CMD} --allow-unauthenticated"
    else
        DEPLOY_CMD="${DEPLOY_CMD} --no-allow-unauthenticated"
    fi
    
    if eval "${DEPLOY_CMD}"; then
        echo -e "${GREEN}✓ Service deployed successfully${NC}"
    else
        echo -e "${RED}✗ Deployment failed${NC}"
        exit 1
    fi
}

# Function to get service URL
get_service_url() {
    echo -e "${BLUE}Getting service URL...${NC}"
    SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
        --region "${REGION}" \
        --format 'value(status.url)')
    
    if [ -n "$SERVICE_URL" ]; then
        echo -e "${GREEN}✓ Service URL: ${SERVICE_URL}${NC}"
    else
        echo -e "${YELLOW}Warning: Could not retrieve service URL${NC}"
    fi
}

# Main execution
main() {
    echo -e "${YELLOW}Starting deployment process...${NC}"
    echo ""
    
    # Check gcloud
    check_gcloud
    
    # Set project
    set_project
    echo ""
    
    # Enable APIs
    enable_apis
    echo ""
    
    # Build image (unless deploy-only)
    if [ "$DEPLOY_ONLY" != "true" ]; then
        build_image
        echo ""
    fi
    
    # Deploy service (unless build-only)
    if [ "$BUILD_ONLY" != "true" ]; then
        deploy_service
        echo ""
        
        # Get service URL
        get_service_url
        echo ""
    fi
    
    echo "================================================"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo "================================================"
    echo ""
    
    if [ "$BUILD_ONLY" != "true" ]; then
        echo "Your application is now running on Google Cloud Run"
        if [ -n "$SERVICE_URL" ]; then
            echo "Access it at: ${SERVICE_URL}"
        fi
        echo ""
        echo "Useful commands:"
        echo "  View logs:"
        echo "    gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=${SERVICE_NAME}\" --limit 50"
        echo ""
        echo "  Stream logs:"
        echo "    gcloud alpha run services logs tail ${SERVICE_NAME} --region ${REGION}"
        echo ""
        echo "  Update service:"
        echo "    gcloud run services update ${SERVICE_NAME} --region ${REGION} [OPTIONS]"
        echo ""
        echo "  Delete service:"
        echo "    gcloud run services delete ${SERVICE_NAME} --region ${REGION}"
    else
        echo "Image built successfully!"
        echo "To deploy, run: ./deploy-cloudrun.sh --project ${PROJECT_ID} --deploy-only"
    fi
}

# Run main function
main

