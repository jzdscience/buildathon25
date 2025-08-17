#!/usr/bin/env python3
"""
Test script for Inbox Triage Assistant
This creates mock data to test the app functionality
"""

import json
from datetime import datetime, timedelta
import random

def create_mock_emails(count=50):
    """Create mock email data for testing"""
    
    # Sample email data
    senders = [
        "Company <noreply@company.com>",
        "Service <notifications@service.com>", 
        "Platform <auto-confirm@platform.com>",
        "Streaming <info@streaming.com>",
        "Search <noreply@search.com>",
        "John Doe <john.doe@example.com>",
        "Jane Smith <jane@example.com>",
        "Calendar <calendar@example.com>",
        "VideoCall <noreply@videocall.com>",
        "Collaboration <noreply@collaboration.com>"
    ]
    
    subjects = [
        "Weekly LinkedIn digest",
        "New job recommendations for you",
        "Your GitHub activity summary", 
        "Pull request needs review",
        "Your Amazon order has shipped",
        "New items recommended for you",
        "New releases on Netflix",
        "Your monthly viewing activity",
        "Security alert for your account",
        "Meeting reminder: Project sync",
        "Calendar: Team standup tomorrow",
        "Zoom: Meeting starting soon",
        "Microsoft Teams: You have new messages",
        "Project deadline approaching",
        "Weekly team update",
        "Invoice for services rendered",
        "Payment confirmation received",
        "Newsletter: Tech Weekly"
    ]
    
    body_templates = [
        "This is an automated email notification...",
        "Hi there! We wanted to update you on...",
        "Important information regarding your account...",
        "Thank you for your recent activity...",
        "Please review the attached documents...",
        "Your weekly summary is ready to view...",
        "New updates are available for...",
        "Security notice: We detected unusual..."
    ]
    
    emails = []
    base_date = datetime.now()
    
    for i in range(count):
        sender = random.choice(senders)
        subject = random.choice(subjects)
        body = random.choice(body_templates) + f" Email #{i+1} content here."
        
        # Create realistic date spread over last 30 days
        days_ago = random.randint(0, 30)
        email_date = base_date - timedelta(days=days_ago)
        
        email = {
            'id': 1000 + i,
            'subject': subject,
            'sender': sender,
            'date': email_date.strftime('%a, %d %b %Y %H:%M:%S %z'),
            'body': body,
            'raw_message': None
        }
        emails.append(email)
    
    return emails

def test_clustering():
    """Test the email clustering functionality"""
    print("🧪 Testing Email Clustering...")
    
    try:
        from email_clusterer import EmailClusterer
        
        # Create mock emails
        emails = create_mock_emails(50)
        print(f"✅ Created {len(emails)} mock emails")
        
        # Test clustering
        clusterer = EmailClusterer(n_clusters=5)
        clusters = clusterer.cluster_emails(emails)
        
        print(f"✅ Successfully clustered emails into {len(clusters)} groups:")
        
        for cluster_id, cluster_data in clusters.items():
            name = cluster_data['name']
            count = cluster_data['count']
            print(f"   📁 {name} ({count} emails)")
            
            # Show sample emails from each cluster
            for email in cluster_data['emails'][:2]:
                subject = email['subject'][:40] + "..." if len(email['subject']) > 40 else email['subject']
                print(f"      • {subject}")
        
        return True
        
    except Exception as e:
        print(f"❌ Clustering test failed: {e}")
        return False

def test_web_endpoints():
    """Test web API endpoints"""
    print("\n🌐 Testing Web API Endpoints...")
    
    import requests
    base_url = "http://localhost:8080"
    
    tests = [
        ("GET", "/", "Main page"),
        ("GET", "/api/status", "Connection status"),
        ("GET", "/api/oauth/config", "OAuth configuration"),
    ]
    
    success_count = 0
    
    for method, endpoint, description in tests:
        try:
            url = base_url + endpoint
            if method == "GET":
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
                success_count += 1
            else:
                print(f"⚠️  {description}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {description}: Failed - {e}")
    
    print(f"\n📊 Web API Tests: {success_count}/{len(tests)} passed")
    return success_count == len(tests)

def main():
    """Run all tests"""
    print("🧪 Inbox Triage Assistant - Test Suite")
    print("=" * 50)
    
    # Test 1: Email Clustering
    clustering_ok = test_clustering()
    
    # Test 2: Web API
    web_ok = test_web_endpoints()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Email Clustering: {'✅ PASS' if clustering_ok else '❌ FAIL'}")
    print(f"   Web API: {'✅ PASS' if web_ok else '❌ FAIL'}")
    
    if clustering_ok and web_ok:
        print("\n🎉 All tests passed! The app is working correctly.")
        print("🔗 Access the app at: http://localhost:8080")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()