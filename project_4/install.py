#!/usr/bin/env python3
"""
Installation script for Codebase Time Machine
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False

def download_nltk_data():
    """Download required NLTK data"""
    print("Downloading NLTK data...")
    try:
        import nltk
        import ssl
        
        # Handle SSL certificate issues
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        # Download required data with explicit success checking
        datasets = ['punkt', 'punkt_tab', 'stopwords', 'vader_lexicon']
        for dataset in datasets:
            print(f"   Downloading {dataset}...")
            result = nltk.download(dataset, quiet=False)
            if not result:
                print(f"   ⚠️  Failed to download {dataset}")
            else:
                print(f"   ✅ {dataset} downloaded")
        
        print("✅ NLTK data download completed!")
        return True
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        print("   You can manually download by running:")
        print("   python3 -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')\"")
        return False

def test_installation():
    """Test if installation was successful"""
    print("Testing installation...")
    try:
        # Test imports
        import git
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import plotly
        import nltk
        import sklearn
        import textblob
        import click
        import rich
        
        print("✅ All imports successful!")
        
        # Test NLTK data (non-critical)
        try:
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            stopwords.words('english')[:5]  # Test access
            word_tokenize("test sentence")  # Test tokenization
            print("✅ NLTK data accessible!")
        except Exception as nltk_error:
            print(f"⚠️  NLTK data issue: {nltk_error}")
            print("   The tool will still work, but some NLP features may be limited.")
            print("   Try running: python3 -c \"import nltk; nltk.download('stopwords'); nltk.download('punkt'); nltk.download('vader_lexicon')\"")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("CODEBASE TIME MACHINE - SETUP")
    print("=" * 60)
    
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if requirements.txt exists
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        print("Make sure you're running this from the project directory.")
        return
    
    # Install packages
    if not install_requirements():
        print("Setup failed during package installation.")
        return
    
    # Download NLTK data
    if not download_nltk_data():
        print("Setup failed during NLTK data download.")
        return
    
    # Test installation
    if not test_installation():
        print("Setup failed during testing.")
        return
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE! 🎉")
    print("=" * 60)
    
    print("\nYou can now use the Codebase Time Machine:")
    print("\n1. Basic usage:")
    print("   python codebase_time_machine.py --repo-url https://github.com/user/repo.git")
    
    print("\n2. Interactive example:")
    print("   python example_usage.py --interactive")
    
    print("\n3. Automated example:")
    print("   python example_usage.py")
    
    print("\n4. Full analysis:")
    print("   python codebase_time_machine.py --repo-path /path/to/repo --full-analysis")
    
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()