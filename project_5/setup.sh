#!/bin/bash

# Setup script for Universal Knowledge-Graph Builder

echo "Setting up Universal Knowledge-Graph Builder..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm

echo "Setup complete! Activate the virtual environment with: source venv/bin/activate"
