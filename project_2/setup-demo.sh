#!/bin/bash

# Voice-to-Slide Generator - Hackathon Demo Setup
# This script helps you quickly set up the OpenAI API key for your demo

set -e

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🎤 Voice-to-Slide Generator - Hackathon Demo Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

# Function to create .env file
create_env_file() {
    echo -e "${YELLOW}📝 Setting up environment configuration...${NC}\n"
    
    if [ -f .env ]; then
        echo -e "${YELLOW}⚠️  .env file already exists. Do you want to overwrite it? (y/n)${NC}"
        read -r response
        if [ "$response" != "y" ]; then
            echo -e "${GREEN}Keeping existing .env file${NC}"
            return
        fi
    fi
    
    echo -e "${YELLOW}Please enter your OpenAI API key:${NC}"
    echo -e "${YELLOW}(Get one from: https://platform.openai.com/api-keys)${NC}"
    read -rs OPENAI_KEY
    echo
    
    if [ -z "$OPENAI_KEY" ]; then
        echo -e "${RED}❌ Error: OpenAI API key is required for the demo${NC}"
        exit 1
    fi
    
    # Create .env file
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=$OPENAI_KEY

# Server Configuration
PORT=3000
NODE_ENV=production
EOF
    
    echo -e "${GREEN}✅ .env file created successfully${NC}\n"
}

# Function to set up for local demo
setup_local_demo() {
    echo -e "${YELLOW}🏠 Setting up for local demo...${NC}\n"
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first${NC}"
        exit 1
    fi
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    npm install
    
    echo -e "\n${GREEN}✅ Local setup complete!${NC}"
    echo -e "${GREEN}To start the demo locally:${NC}"
    echo -e "${BLUE}npm start${NC}"
    echo -e "${GREEN}Then open: ${YELLOW}http://localhost:3000${NC}\n"
}

# Function to set up for Cloud Run demo
setup_cloud_demo() {
    echo -e "${YELLOW}☁️  Setting up for Google Cloud Run demo...${NC}\n"
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ gcloud CLI is not installed${NC}"
        echo -e "${YELLOW}Install from: https://cloud.google.com/sdk/docs/install${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Enter your Google Cloud Project ID:${NC}"
    read -r PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}❌ Project ID is required${NC}"
        exit 1
    fi
    
    # Read API key from .env
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found. Please run this script again and create it first${NC}"
        exit 1
    fi
    
    source .env
    
    echo -e "${YELLOW}🔐 Setting up Google Secret Manager...${NC}"
    
    # Set project
    gcloud config set project "$PROJECT_ID"
    
    # Enable required APIs
    echo -e "${YELLOW}Enabling required APIs...${NC}"
    gcloud services enable secretmanager.googleapis.com cloudbuild.googleapis.com run.googleapis.com
    
    # Create or update secret
    echo -e "${YELLOW}Storing API key in Secret Manager...${NC}"
    if gcloud secrets describe openai-api-key --project="$PROJECT_ID" &>/dev/null; then
        echo -n "$OPENAI_API_KEY" | gcloud secrets versions add openai-api-key --data-file=-
    else
        echo -n "$OPENAI_API_KEY" | gcloud secrets create openai-api-key \
            --data-file=- \
            --replication-policy="automatic"
    fi
    
    echo -e "\n${GREEN}✅ Cloud setup complete!${NC}"
    echo -e "${GREEN}To deploy to Cloud Run:${NC}"
    echo -e "${BLUE}./deploy.sh${NC}"
    echo -e "${YELLOW}Or for quick redeploy:${NC}"
    echo -e "${BLUE}./redeploy.sh${NC}\n"
}

# Function to set up for Docker demo
setup_docker_demo() {
    echo -e "${YELLOW}🐳 Setting up for Docker demo...${NC}\n"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo -e "${YELLOW}Install from: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    # Read API key from .env
    if [ ! -f .env ]; then
        echo -e "${RED}❌ .env file not found. Please run this script again and create it first${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker setup complete!${NC}"
    echo -e "${GREEN}To run with Docker:${NC}"
    echo -e "${BLUE}docker-compose up${NC}"
    echo -e "${YELLOW}Or build and run manually:${NC}"
    echo -e "${BLUE}docker build -t voice-to-slide .${NC}"
    echo -e "${BLUE}docker run -p 8080:8080 --env-file .env voice-to-slide${NC}\n"
}

# Main menu
echo -e "${YELLOW}Select your demo environment:${NC}"
echo -e "1) Local development (npm)"
echo -e "2) Docker container"
echo -e "3) Google Cloud Run"
echo -e "4) Just create .env file"
echo -e "5) Exit"
echo
read -p "Enter your choice (1-5): " choice

# Always create .env first (except for exit)
if [ "$choice" != "5" ]; then
    create_env_file
fi

case $choice in
    1)
        setup_local_demo
        ;;
    2)
        setup_docker_demo
        ;;
    3)
        setup_cloud_demo
        ;;
    4)
        echo -e "${GREEN}✅ Setup complete!${NC}"
        echo -e "${YELLOW}Your .env file has been created with the OpenAI API key${NC}"
        ;;
    5)
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Your Voice-to-Slide Generator is ready for the hackathon!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}📋 Quick Reference:${NC}"
echo -e "• OpenAI API key is stored in .env file"
echo -e "• Test with a 1-3 minute audio recording"
echo -e "• Supports MP3, WAV, M4A, OGG, WebM formats"
echo -e "• Generates 5-8 slides with speaker notes"
echo -e "• Exports as HTML and PDF\n"

echo -e "${YELLOW}⚠️  Security Reminder:${NC}"
echo -e "• Never commit .env file to git"
echo -e "• Add .env to .gitignore"
echo -e "• For production, use environment variables or secret managers"
echo -e "• Rotate API keys after the hackathon\n"

echo -e "${GREEN}Good luck with your hackathon demo! 🚀${NC}"


