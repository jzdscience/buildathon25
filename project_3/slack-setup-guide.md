# Slack App Setup Guide for Employee Engagement Pulse

## Quick Reference: Required Tokens

After completing the setup, you'll need these two tokens:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here      # From OAuth & Permissions
SLACK_APP_TOKEN=xapp-your-app-token-here      # From Socket Mode
```

## Step-by-Step Setup

### 1. Create Slack App
- Go to https://api.slack.com/apps
- Click "Create New App" → "From scratch"
- Name: "Employee Engagement Pulse"
- Select your workspace

### 2. Add Bot Token Scopes (OAuth & Permissions)
Required scopes:
- `channels:history` - View messages in public channels
- `channels:read` - View basic information about public channels
- `chat:read` - View messages in channels and conversations
- `reactions:read` - View emoji reactions
- `users:read` - View people in workspace

### 3. Install to Workspace
- Click "Install to Workspace"
- Copy the Bot User OAuth Token (starts with `xoxb-`)

### 4. Enable Socket Mode
- Go to Socket Mode in sidebar
- Toggle "Enable Socket Mode" ON
- Generate app-level token with `connections:write` scope
- Copy the token (starts with `xapp-`)

### 5. Add Bot to Channels
- Go to your Slack workspace
- In each channel you want to monitor:
  - Type: `/invite @Employee Engagement Pulse`
  - Or use the app name you chose

## Testing Your Setup

1. Update your `.env` file with both tokens
2. Run `./verify-setup.sh` to check configuration
3. Run `./start-dev.sh` to start the application
4. Go to Settings → Test Slack Connection
5. Should show: "Connected as [bot-name] in [workspace]"

## Troubleshooting

### "Invalid Auth" Error
- Check that SLACK_BOT_TOKEN starts with `xoxb-`
- Verify the bot is installed in your workspace

### "Socket Mode" Connection Issues  
- Check that SLACK_APP_TOKEN starts with `xapp-`
- Ensure Socket Mode is enabled in your Slack app

### "Missing Scopes" Error
- Verify all 5 OAuth scopes are added
- Reinstall the app after adding scopes

### No Messages Detected
- Invite the bot to channels: `/invite @YourBotName`
- Check that the bot appears in channel member list
- Verify channels are public (not private)

