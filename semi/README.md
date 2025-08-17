# Inbox Triage Assistant

A Python tool that clusters your Gmail inbox into actionable groups and enables one-click archiving per cluster. Available in both CLI and Web UI versions.

## Features

- 🔐 **Gmail IMAP Authentication** - Secure connection to your Gmail account
- 📧 **Smart Email Clustering** - Groups your last 200 emails into descriptive clusters
- 🎯 **Intelligent Categorization** - Automatically identifies email types (promotional, meetings, notifications, etc.)
- 📱 **One-Click Archive** - Archive entire clusters with a single command
- 🎨 **Modern Web UI** - Beautiful, responsive web interface with real-time updates
- 💻 **CLI Interface** - Command-line version for terminal users
- 📊 **Visual Email Previews** - See email subjects, senders, and content previews
- 🔄 **Real-time Refresh** - Update clusters without restarting the application

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Gmail App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Generate an App Password for "Mail"
   - **Important:** Use an App Password, not your regular Gmail password

## Usage

### Web UI (Recommended)

1. **Start the web application:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   - Navigate to http://localhost:5000
   - Enter your Gmail credentials directly in the web interface
   - No need for a .env file when using the web UI

3. **Use the interface:**
   - View beautifully organized email clusters
   - See email previews with subjects, senders, and content
   - Archive entire clusters with confirmation dialogs
   - Real-time status updates and notifications

### CLI Version

1. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Configure Gmail credentials:**
   - Edit `.env` file with your Gmail username and app password

3. **Run the CLI:**
   ```bash
   python main.py
   ```

## How It Works

1. Connects to your Gmail account via IMAP
2. Fetches your last 200 emails from the inbox
3. Uses machine learning (TF-IDF + K-means) to cluster emails by similarity
4. Generates descriptive cluster names like:
   - "Emails from LinkedIn" 
   - "Promotional Emails"
   - "Meeting & Events"
   - "Notifications & Updates"
5. Allows you to archive entire clusters with one click
6. Moves emails to "All Mail" folder (safe archiving, no deletion)

## Security

- Uses Gmail's official IMAP API
- Requires App Password (more secure than regular password)
- No email content is stored locally
- Only archives emails (moves to All Mail, doesn't delete)

## Requirements

- Python 3.7+
- Gmail account with IMAP enabled
- App Password generated for your Google account