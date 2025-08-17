#!/usr/bin/env python3

import os
import sys
from web_api import app

def main():
    print("🚀 Starting Inbox Triage Assistant Web UI...")
    print("📧 Access the application at: http://localhost:8080")
    print("⚠️  Make sure you have your Gmail App Password ready!")
    print("🔐 Generate one at: https://myaccount.google.com/apppasswords")
    print("-" * 60)
    
    try:
        port = int(os.environ.get('PORT', 8080))
        debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
        app.run(debug=debug, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Inbox Triage Assistant...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()