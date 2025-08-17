#!/usr/bin/env python3

import sys
import os
from cli_interface import CLIInterface

def main():
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("📝 Please create a .env file with your Gmail credentials:")
        print("   GMAIL_USERNAME=your_email@gmail.com")
        print("   GMAIL_PASSWORD=your_app_password")
        print("\n🔐 Note: Use an App Password, not your regular Gmail password.")
        print("   Generate one at: https://myaccount.google.com/apppasswords")
        sys.exit(1)
    
    try:
        cli = CLIInterface()
        cli.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()