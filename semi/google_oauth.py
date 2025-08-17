import os
import json
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

class GoogleOAuthManager:
    def __init__(self):
        # OAuth 2.0 configuration for Gmail access
        self.client_config = {
            "web": {
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/oauth/callback"]
            }
        }
        
        # Gmail scopes needed for IMAP access
        self.scopes = [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify',
            'openid',
            'email',
            'profile'
        ]
        
        self.redirect_uri = "http://localhost:8080/oauth/callback"
    
    def get_authorization_url(self) -> Optional[str]:
        """Generate Google OAuth authorization URL"""
        try:
            if not self.client_config["web"]["client_id"]:
                return None
                
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return authorization_url
        except Exception as e:
            print(f"Error generating auth URL: {e}")
            return None
    
    def exchange_code_for_tokens(self, auth_code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access tokens"""
        try:
            if not self.client_config["web"]["client_id"]:
                return None
                
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for tokens
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # Get user profile info
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            
            return {
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
            
        except Exception as e:
            print(f"Error exchanging code for tokens: {e}")
            return None
    
    def get_app_password_instructions(self) -> str:
        """Return instructions for generating an app password"""
        return """
        To use Gmail with this application, you'll need to generate an App Password:
        
        1. Go to your Google Account settings: https://myaccount.google.com/security
        2. Enable 2-Step Verification if not already enabled
        3. Go to App passwords: https://myaccount.google.com/apppasswords
        4. Select 'Mail' and generate a password
        5. Use that 16-character password (remove spaces) in the manual login form
        
        Note: OAuth login will authenticate you but you'll still need an App Password 
        for IMAP access since Google requires it for third-party email clients.
        """
    
    def is_configured(self) -> bool:
        """Check if OAuth is properly configured"""
        return bool(
            self.client_config["web"]["client_id"] and 
            self.client_config["web"]["client_secret"]
        )