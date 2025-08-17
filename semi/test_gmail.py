#!/usr/bin/env python3

import sys
import os
from gmail_client import GmailClient

def test_gmail_connection():
    print("🔍 Gmail Connection Test")
    print("=" * 40)
    
    # Get credentials from user
    username = input("Enter your Gmail address: ")
    password = input("Enter your App Password: ")
    
    print(f"\n📧 Testing connection for: {username}")
    print("-" * 40)
    
    # Set environment variables
    os.environ['GMAIL_USERNAME'] = username
    os.environ['GMAIL_PASSWORD'] = password
    
    # Test connection
    try:
        client = GmailClient()
        if client.connect():
            print("✅ SUCCESS: Connected to Gmail!")
            
            # Test fetching emails
            print("📬 Testing email fetch...")
            emails = client.fetch_recent_emails(5)
            print(f"📊 Found {len(emails)} emails")
            
            if emails:
                print("\n📧 First email preview:")
                email = emails[0]
                print(f"   Subject: {email['subject'][:50]}...")
                print(f"   From: {email['sender'][:50]}...")
            
            client.disconnect()
            print("🔚 Disconnected successfully")
            
        else:
            print("❌ FAILED: Could not connect to Gmail")
            print("\n🔧 Troubleshooting:")
            print("1. Make sure you're using an App Password (not regular password)")
            print("2. Generate App Password at: https://myaccount.google.com/apppasswords")
            print("3. Enable IMAP in Gmail Settings > Forwarding and POP/IMAP")
            print("4. Make sure 2-Factor Authentication is enabled")
            
    except Exception as e:
        print(f"💥 ERROR: {e}")

if __name__ == "__main__":
    test_gmail_connection()