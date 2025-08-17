#!/bin/bash

# Local Development/Demo Script for Knowledge Graph Builder
# This script sets up and runs the application locally

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Knowledge Graph Builder - Local Demo Setup${NC}"
echo "============================================"
echo ""

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Check if dependencies are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Installing dependencies (this may take a few minutes)...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${GREEN}✓ Dependencies already installed${NC}"
fi

# Check if spaCy model is installed
echo -e "${YELLOW}Checking spaCy language model...${NC}"
if ! python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo -e "${YELLOW}Downloading spaCy model...${NC}"
    python -m spacy download en_core_web_sm
    echo -e "${GREEN}✓ spaCy model downloaded${NC}"
else
    echo -e "${GREEN}✓ spaCy model already installed${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating necessary directories...${NC}"
mkdir -p uploads graphs static templates
echo -e "${GREEN}✓ Directories created${NC}"

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export PORT=5000

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Setup complete! Starting application...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Application will be available at:${NC}"
echo -e "${GREEN}http://localhost:5000${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Run the application
python app.py

