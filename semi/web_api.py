from flask import Flask, render_template, jsonify, request, redirect, session, url_for
from flask_cors import CORS
import threading
import time
import os
from gmail_client import GmailClient
from email_clusterer import EmailClusterer
from google_oauth import GoogleOAuthManager

app = Flask(__name__)
CORS(app)

# Production configuration
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Use environment variable for secret key in production, with fallback for development
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

import logging
logging.basicConfig(level=logging.DEBUG)

gmail_client = None
clusterer = EmailClusterer()
cached_clusters = {}
connection_status = {"connected": False, "error": None}
oauth_manager = GoogleOAuthManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/oauth/config')
def oauth_config():
    """Get OAuth configuration status"""
    return jsonify({
        "available": oauth_manager.is_configured(),
        "instructions": oauth_manager.get_app_password_instructions()
    })

@app.route('/api/oauth/authorize')
def oauth_authorize():
    """Start OAuth flow"""
    if not oauth_manager.is_configured():
        return jsonify({
            "success": False, 
            "error": "OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
        })
    
    auth_url = oauth_manager.get_authorization_url()
    if auth_url:
        return jsonify({"success": True, "auth_url": auth_url})
    else:
        return jsonify({"success": False, "error": "Failed to generate authorization URL"})

@app.route('/oauth/callback')
def oauth_callback():
    """Handle OAuth callback"""
    auth_code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return f"<h1>OAuth Error</h1><p>{error}</p><script>window.close();</script>"
    
    if not auth_code:
        return "<h1>OAuth Error</h1><p>No authorization code received</p><script>window.close();</script>"
    
    # Exchange code for tokens
    tokens = oauth_manager.exchange_code_for_tokens(auth_code)
    
    if tokens:
        # Store user info in session
        session['user_email'] = tokens['email']
        session['user_name'] = tokens['name']
        session['oauth_completed'] = True
        
        return f"""
        <h1>✅ Authentication Successful!</h1>
        <p>Welcome, {tokens['name']} ({tokens['email']})</p>
        <p>You can now close this window and return to the app.</p>
        <p><strong>Note:</strong> You'll still need to enter an App Password for Gmail IMAP access.</p>
        <script>
            window.opener.postMessage({{
                type: 'oauth_success',
                user: {{
                    email: '{tokens['email']}',
                    name: '{tokens['name']}',
                    picture: '{tokens.get('picture', '')}'
                }}
            }}, '*');
            window.close();
        </script>
        """
    else:
        return "<h1>OAuth Error</h1><p>Failed to exchange authorization code</p><script>window.close();</script>"

@app.route('/api/connect', methods=['POST'])
def connect_gmail():
    global gmail_client, connection_status
    
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password required"})
        
        import os
        os.environ['GMAIL_USERNAME'] = username
        os.environ['GMAIL_PASSWORD'] = password
        
        print(f"🔍 DEBUG: Attempting connection for {username}", flush=True)
        gmail_client = GmailClient()
        
        if gmail_client.connect():
            print("✅ DEBUG: Gmail connection successful")
            connection_status = {"connected": True, "error": None}
            return jsonify({"success": True})
        else:
            print("❌ DEBUG: Gmail connection failed")
            # Provide more helpful error messages
            error_message = "Failed to connect to Gmail. Common issues:\n"
            error_message += "1. Make sure you're using an App Password (not your regular password)\n"
            error_message += "2. Generate App Password at: https://myaccount.google.com/apppasswords\n"
            error_message += "3. Enable IMAP in Gmail Settings > Forwarding and POP/IMAP\n"
            error_message += "4. Make sure 2-Factor Authentication is enabled on your Google account"
            
            connection_status = {"connected": False, "error": error_message}
            return jsonify({"success": False, "error": error_message})
    
    except Exception as e:
        connection_status = {"connected": False, "error": str(e)}
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/status')
def get_status():
    return jsonify(connection_status)

@app.route('/api/clusters')
def get_clusters():
    global gmail_client, cached_clusters
    
    if not gmail_client or not connection_status["connected"]:
        return jsonify({"success": False, "error": "Not connected to Gmail"})
    
    try:
        emails = gmail_client.fetch_recent_emails(200)
        
        if not emails:
            return jsonify({"success": False, "error": "No emails found"})
        
        clusters = clusterer.cluster_emails(emails)
        
        formatted_clusters = []
        for cluster_id, cluster_data in clusters.items():
            formatted_clusters.append({
                "id": cluster_id,
                "name": cluster_data["name"],
                "count": cluster_data["count"],
                "emails": [
                    {
                        "id": email["id"],
                        "subject": email["subject"],
                        "sender": email["sender"],
                        "date": email["date"],
                        "body_preview": email["body"][:150] + "..." if len(email["body"]) > 150 else email["body"]
                    }
                    for email in cluster_data["emails"]
                ]
            })
        
        cached_clusters = clusters
        return jsonify({"success": True, "clusters": formatted_clusters})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/archive', methods=['POST'])
def archive_cluster():
    global gmail_client, cached_clusters
    
    if not gmail_client or not connection_status["connected"]:
        return jsonify({"success": False, "error": "Not connected to Gmail"})
    
    try:
        data = request.get_json()
        cluster_id = data.get('cluster_id')
        
        if cluster_id is None or cluster_id not in cached_clusters:
            return jsonify({"success": False, "error": "Invalid cluster ID"})
        
        cluster_data = cached_clusters[cluster_id]
        email_ids = [email['id'] for email in cluster_data['emails']]
        
        if gmail_client.archive_emails(email_ids):
            return jsonify({
                "success": True, 
                "message": f"Successfully archived {len(email_ids)} emails from '{cluster_data['name']}'"
            })
        else:
            return jsonify({"success": False, "error": "Failed to archive emails"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_gmail():
    global gmail_client, connection_status, cached_clusters
    
    try:
        if gmail_client:
            gmail_client.disconnect()
        
        gmail_client = None
        connection_status = {"connected": False, "error": None}
        cached_clusters = {}
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # This is only used for local development
    # In production, gunicorn serves the app
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=port)