#!/bin/bash

echo "=========================================="
echo "CODEBASE TIME MACHINE - INSTALLATION"
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip is required but not found."
    echo "Please install pip and try again."
    exit 1
fi

echo "✅ pip found"

# Install requirements
echo ""
echo "Installing Python packages..."
if python3 -m pip install -r requirements.txt; then
    echo "✅ Packages installed successfully!"
else
    echo "❌ Failed to install packages. Try running:"
    echo "   python3 -m pip install --user -r requirements.txt"
    exit 1
fi

# Test installation by running the install.py script
echo ""
echo "Running post-installation setup..."
if python3 install.py; then
    echo ""
    echo "=========================================="
    echo "INSTALLATION COMPLETE! 🎉"
    echo "=========================================="
    echo ""
    echo "You can now use the Codebase Time Machine:"
    echo ""
    echo "1. Basic usage:"
    echo "   python3 codebase_time_machine.py --repo-url https://github.com/user/repo.git"
    echo ""
    echo "2. Interactive example:"
    echo "   python3 example_usage.py --interactive"
    echo ""
    echo "3. Automated example:"
    echo "   python3 example_usage.py"
    echo ""
    echo "For more information, see README.md"
else
    echo "❌ Post-installation setup failed."
    echo "You may still be able to use the tool, but some features might not work."
fi