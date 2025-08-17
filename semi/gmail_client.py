import os
import email
from datetime import datetime
from typing import List, Dict, Any
from imapclient import IMAPClient
from dotenv import load_dotenv

load_dotenv()

class GmailClient:
    def __init__(self):
        self.username = os.getenv('GMAIL_USERNAME')
        self.password = os.getenv('GMAIL_PASSWORD')
        self.client = None
        
        if not self.username or not self.password:
            raise ValueError("Please set GMAIL_USERNAME and GMAIL_PASSWORD in your .env file")
    
    def connect(self):
        try:
            print(f"Attempting to connect to Gmail for user: {self.username}")
            import ssl
            context = ssl.create_default_context()
            # For testing purposes, allow unverified SSL (not recommended for production)
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            self.client = IMAPClient('imap.gmail.com', use_uid=True, ssl=True, port=993, ssl_context=context)
            print("IMAP client created, attempting login...")
            self.client.login(self.username, self.password)
            print("Successfully logged in to Gmail")
            return True
        except Exception as e:
            error_msg = str(e).lower()
            print(f"Gmail connection failed: {e}")
            
            if "authentication failed" in error_msg or "invalid credentials" in error_msg:
                print("ERROR: Authentication failed - Check your App Password")
                print("Make sure you're using an App Password, not your regular Gmail password")
                print("Generate one at: https://myaccount.google.com/apppasswords")
            elif "connection refused" in error_msg or "network" in error_msg:
                print("ERROR: Network connection failed")
                print("Check your internet connection and firewall settings")
            elif "imap access" in error_msg or "disabled" in error_msg:
                print("ERROR: IMAP access disabled")
                print("Enable IMAP in Gmail Settings > Forwarding and POP/IMAP")
            else:
                print(f"ERROR: Unexpected error - {e}")
            
            return False
    
    def disconnect(self):
        if self.client:
            self.client.logout()
    
    def fetch_recent_emails(self, count: int = 200) -> List[Dict[str, Any]]:
        if not self.client:
            raise RuntimeError("Not connected to Gmail")
        
        self.client.select_folder('INBOX')
        
        messages = self.client.search(['NOT', 'DELETED'])
        recent_messages = messages[-count:] if len(messages) > count else messages
        
        emails = []
        for msg_id in recent_messages:
            response = self.client.fetch([msg_id], ['RFC822'])
            raw_email = response[msg_id][b'RFC822']
            email_message = email.message_from_bytes(raw_email)
            
            subject = email_message.get('Subject', 'No Subject')
            sender = email_message.get('From', 'Unknown Sender')
            date_str = email_message.get('Date', '')
            
            body = self._extract_body(email_message)
            
            emails.append({
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'date': date_str,
                'body': body[:500],
                'raw_message': email_message
            })
        
        return emails
    
    def archive_emails(self, email_ids: List[int]) -> bool:
        if not self.client:
            raise RuntimeError("Not connected to Gmail")
        
        try:
            self.client.select_folder('INBOX')
            self.client.move(email_ids, '[Gmail]/All Mail')
            return True
        except Exception as e:
            print(f"Failed to archive emails: {e}")
            return False
    
    def _extract_body(self, email_message) -> str:
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body.strip()