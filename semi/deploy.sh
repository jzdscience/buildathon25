#!/bin/bash

# Inbox Triage Assistant - Google Cloud Run Deployment Script
# This script simplifies the deployment process to Google Cloud Run

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
REGION="us-central1"
SERVICE_NAME="inbox-triage-assistant"
MEMORY="512Mi"
CPU="1"
MIN_INSTANCES="0"
MAX_INSTANCES="10"

# Function to print colored output
print_message() {
    echo -e "${2}${1}${NC}"
}

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_message "❌ gcloud CLI is not installed. Please install it first:" "$RED"
        print_message "Visit: https://cloud.google.com/sdk/docs/install" "$YELLOW"
        exit 1
    fi
    print_message "✅ gcloud CLI is installed" "$GREEN"
}

# Function to check authentication
check_auth() {
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_message "⚠️  You are not authenticated with gcloud" "$YELLOW"
        print_message "Running: gcloud auth login" "$YELLOW"
        gcloud auth login
    fi
    print_message "✅ Authenticated with Google Cloud" "$GREEN"
}

# Function to select or create project
setup_project() {
    print_message "\n📋 Current project: $(gcloud config get-value project 2>/dev/null || echo 'None')" "$YELLOW"
    
    read -p "Do you want to use the current project? (y/n): " use_current
    
    if [[ $use_current != "y" ]]; then
        print_message "\nAvailable projects:" "$YELLOW"
        gcloud projects list
        
        read -p "Enter project ID (or 'new' to create): " project_id
        
        if [[ $project_id == "new" ]]; then
            read -p "Enter new project ID: " new_project_id
            read -p "Enter project name: " project_name
            gcloud projects create "$new_project_id" --name="$project_name"
            project_id=$new_project_id
        fi
        
        gcloud config set project "$project_id"
    fi
    
    PROJECT_ID=$(gcloud config get-value project)
    print_message "✅ Using project: $PROJECT_ID" "$GREEN"
}

# Function to enable required APIs
enable_apis() {
    print_message "\n🔧 Enabling required APIs..." "$YELLOW"
    
    apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "containerregistry.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_message "Enabling $api..." "$YELLOW"
        gcloud services enable "$api" --quiet
    done
    
    print_message "✅ All required APIs enabled" "$GREEN"
}

# Function to deploy the application
deploy_app() {
    print_message "\n🚀 Deploying to Cloud Run..." "$YELLOW"
    
    # Check if user wants to customize deployment
    read -p "Use default configuration? (y/n): " use_defaults
    
    if [[ $use_defaults != "y" ]]; then
        read -p "Service name [$SERVICE_NAME]: " input
        SERVICE_NAME=${input:-$SERVICE_NAME}
        
        read -p "Region [$REGION]: " input
        REGION=${input:-$REGION}
        
        read -p "Memory [$MEMORY]: " input
        MEMORY=${input:-$MEMORY}
        
        read -p "CPU [$CPU]: " input
        CPU=${input:-$CPU}
        
        read -p "Min instances [$MIN_INSTANCES]: " input
        MIN_INSTANCES=${input:-$MIN_INSTANCES}
        
        read -p "Max instances [$MAX_INSTANCES]: " input
        MAX_INSTANCES=${input:-$MAX_INSTANCES}
    fi
    
    print_message "\nDeployment configuration:" "$YELLOW"
    print_message "  Service: $SERVICE_NAME" "$NC"
    print_message "  Region: $REGION" "$NC"
    print_message "  Memory: $MEMORY" "$NC"
    print_message "  CPU: $CPU" "$NC"
    print_message "  Min instances: $MIN_INSTANCES" "$NC"
    print_message "  Max instances: $MAX_INSTANCES" "$NC"
    
    # Deploy using source code
    print_message "\n📦 Building and deploying from source..." "$YELLOW"
    
    gcloud run deploy "$SERVICE_NAME" \
        --source . \
        --region "$REGION" \
        --allow-unauthenticated \
        --port 8080 \
        --memory "$MEMORY" \
        --cpu "$CPU" \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --set-env-vars="PORT=8080,FLASK_DEBUG=False" \
        --quiet
    
    # Get the service URL
    SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format="value(status.url)")
    
    print_message "\n✅ Deployment successful!" "$GREEN"
    print_message "🌐 Your app is available at: $SERVICE_URL" "$GREEN"
}

# Function to set up environment variables
setup_env_vars() {
    print_message "\n🔐 Environment Variables Setup" "$YELLOW"
    
    read -p "Do you want to set up OAuth credentials? (y/n): " setup_oauth
    
    if [[ $setup_oauth == "y" ]]; then
        read -p "Enter GOOGLE_CLIENT_ID: " client_id
        read -p "Enter GOOGLE_CLIENT_SECRET: " client_secret
        
        # Generate a secure secret key
        SECRET_KEY=$(openssl rand -hex 32)
        
        gcloud run services update "$SERVICE_NAME" \
            --set-env-vars="GOOGLE_CLIENT_ID=$client_id,GOOGLE_CLIENT_SECRET=$client_secret,SECRET_KEY=$SECRET_KEY" \
            --region "$REGION" \
            --quiet
        
        print_message "✅ OAuth credentials configured" "$GREEN"
    fi
}

# Main deployment flow
main() {
    print_message "🎯 Inbox Triage Assistant - Cloud Run Deployment" "$GREEN"
    print_message "================================================\n" "$GREEN"
    
    # Check prerequisites
    check_gcloud
    check_auth
    
    # Setup project
    setup_project
    
    # Enable APIs
    enable_apis
    
    # Deploy application
    deploy_app
    
    # Optional: Setup environment variables
    setup_env_vars
    
    print_message "\n🎉 Deployment complete!" "$GREEN"
    print_message "📚 For more information, see DEPLOYMENT.md" "$YELLOW"
    
    # Show useful commands
    print_message "\n📌 Useful commands:" "$YELLOW"
    print_message "View logs: gcloud run services logs read $SERVICE_NAME --region $REGION" "$NC"
    print_message "Stream logs: gcloud run services logs tail $SERVICE_NAME --region $REGION" "$NC"
    print_message "Update service: gcloud run services update $SERVICE_NAME --region $REGION" "$NC"
    print_message "Delete service: gcloud run services delete $SERVICE_NAME --region $REGION" "$NC"
}

# Run the main function
main

