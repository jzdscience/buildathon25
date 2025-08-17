# Employee Engagement Pulse 📊

A comprehensive real-time sentiment analysis dashboard that monitors Slack channels to provide managers with actionable insights about team engagement, mood trends, and burnout risk indicators.

**✨ Perfect for Prototyping**: This application runs directly on your local machine without Docker - just Python and Node.js required!

## 🏃‍♂️ TL;DR - Get Started in 3 Commands

```bash
./setup-dev.sh     # One-time setup (installs everything)
# Edit .env with your Slack credentials
./start-dev.sh     # Start the application
```

Then open http://localhost:3000 to see your team sentiment dashboard!

## 🚀 Features

### Core Functionality
- **Real-time Slack monitoring** - Automatically analyzes messages, threads, and reactions
- **Advanced sentiment analysis** - Combines text analysis with emoji sentiment scoring
- **Burnout detection** - Identifies at-risk team members using AI-powered indicators
- **Team engagement metrics** - Tracks participation rates and interaction patterns
- **Weekly trend analysis** - Generates actionable insights for management decisions

### Dashboard Capabilities
- **Interactive sentiment charts** - Visual trends over configurable time periods
- **Channel-specific analytics** - Performance breakdown by Slack channel
- **Burnout alerts** - Priority-based warning system for team wellbeing
- **Manager recommendations** - AI-generated actionable insights
- **Real-time monitoring status** - Live system health and data collection status

## 🛠 Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - Database ORM with SQLite for simplicity
- **Slack SDK** - Official Slack API integration with real-time events
- **TextBlob** - Natural language processing for sentiment analysis
- **APScheduler** - Background task scheduling for data processing

### Frontend
- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development experience
- **Tailwind CSS** - Utility-first styling with custom design system
- **Recharts** - Interactive data visualization components
- **Axios** - HTTP client with comprehensive error handling

### Deployment
- **Docker** - Containerized deployment with multi-stage builds
- **Docker Compose** - Orchestrated services with environment management
- **Health checks** - Built-in monitoring and auto-recovery

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** and **Node.js 16+** installed
- Slack workspace with admin access
- Slack app credentials (Bot Token and App Token)

### 1. Clone the Repository
```bash
git clone <repository-url>
cd employee-engagement-pulse
```

### 2. Local Development Setup (Recommended for Prototyping)

```bash
# One-command setup
./setup-dev.sh

# Follow the prompts to configure your Slack credentials
# Then start the application
./start-dev.sh
```

### 3. Access the Application
- **Frontend**: [http://localhost:3000](http://localhost:3000) - React development server
- **Backend API**: [http://localhost:8000](http://localhost:8000) - FastAPI server
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs) - Interactive API documentation

---

## 🐳 Alternative: Docker Deployment

### Prerequisites for Docker
- Docker and Docker Compose installed

### Docker Quick Start
```bash
# Copy environment template
cp backend/env.template .env

# Edit .env with your Slack credentials
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here

# Start with Docker Compose
docker-compose up -d

# Access at http://localhost:8000
```

---

## 🔧 Slack Integration Setup

### Create a Slack App
1. Visit [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Name your app (e.g., "Employee Engagement Pulse")
4. Select your workspace

### Configure Bot Permissions
Add these OAuth scopes under "OAuth & Permissions":
```
channels:history    - Read public channel messages
channels:read       - View basic information about public channels
chat:read           - View messages in channels and conversations
reactions:read      - View emoji reactions
users:read          - View people in workspace
```

### Enable Socket Mode
1. Go to "Socket Mode" in your app settings
2. Enable Socket Mode
3. Generate an app-level token with `connections:write` scope

### Install App to Workspace
1. Go to "OAuth & Permissions"
2. Click "Install to Workspace"
3. Authorize the app

## 📖 Usage Guide

### Initial Setup
1. **Test Slack Connection** - Go to Settings → Slack Integration to verify connectivity
2. **Add Channels** - Navigate to Channels page and add Slack channels to monitor
3. **Start Monitoring** - Use Settings page to activate real-time monitoring
4. **View Dashboard** - Return to Dashboard to see sentiment analysis in real-time

### Recommended Channels to Monitor
- `#general` - Overall team discussions
- `#random` - Casual team interactions
- `#standups` - Daily team updates
- Project-specific channels
- Team-specific channels

### Understanding the Dashboard

#### Sentiment Metrics
- **Positive sentiment** (0.1 to 1.0): Green indicators, happy team mood
- **Neutral sentiment** (-0.1 to 0.1): Gray indicators, balanced interactions
- **Negative sentiment** (-1.0 to -0.1): Orange/Red indicators, potential concerns

#### Burnout Indicators
- **Risk Score**: Calculated from message sentiment, frequency, and explicit keywords
- **At-Risk Users**: Team members showing concerning patterns
- **Trend Analysis**: Sentiment changes over time periods

#### Engagement Metrics
- **Message Volume**: Daily communication frequency
- **Response Rate**: Percentage of messages with replies or reactions
- **Thread Participation**: Depth of conversations

## 🔧 Advanced Configuration

### Development Options

#### Option 1: Full Development Mode (Recommended for Prototyping)
```bash
./setup-dev.sh      # One-time setup
./start-dev.sh      # Start both backend and frontend with hot reload
```
- Backend: http://localhost:8000 (API only)
- Frontend: http://localhost:3000 (React dev server)
- Hot reload for both backend and frontend changes

#### Option 2: Individual Services
```bash
./start-backend.sh  # Start only backend (port 8000)
./start-frontend.sh # Start only frontend (port 3000)
```

#### Option 3: Production Mode (Single Server)
```bash
./build-production.sh   # Build frontend for production
./start-production.sh   # Serve both from backend on port 8000
```

### Environment Variables
```bash
# Slack API Configuration
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# Analysis Settings
SENTIMENT_UPDATE_INTERVAL_MINUTES=60    # How often to process new data
BURNOUT_THRESHOLD=-0.3                  # Sentiment score triggering burnout alerts
WARNING_THRESHOLD=-0.5                  # Sentiment score for high-priority warnings

# Database Configuration
DATABASE_URL=sqlite:///./data/engagement_pulse.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Security
SECRET_KEY=your-secret-key-here
```

### Database Options
```bash
# Default: SQLite (perfect for prototyping)
DATABASE_URL=sqlite:///./data/engagement_pulse.db

# Production: PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/engagement_pulse

# In-memory (testing only)
DATABASE_URL=sqlite:///:memory:
```

## 📊 API Documentation

### REST API Endpoints
- `GET /api/v1/dashboard` - Dashboard data with sentiment trends
- `GET /api/v1/channels` - List monitored channels
- `POST /api/v1/channels` - Add new channel to monitor
- `DELETE /api/v1/channels/{id}` - Remove channel from monitoring
- `GET /api/v1/monitoring/status` - Real-time monitoring status
- `POST /api/v1/analytics/daily-stats` - Trigger daily statistics generation

### Interactive API Documentation
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI

## 🔒 Security Considerations

### Production Deployment
1. **Change default secrets** - Update SECRET_KEY and other credentials
2. **Use HTTPS** - Configure SSL certificates for production
3. **Database security** - Use PostgreSQL with proper access controls
4. **Network isolation** - Deploy behind a reverse proxy
5. **Regular updates** - Keep dependencies and base images updated

### Data Privacy
- **Message content** is analyzed for sentiment but not stored permanently
- **User IDs** are anonymized in reports and recommendations
- **Compliance** with workplace privacy policies is recommended

## 🛠 Development

### Quick Development Setup
```bash
# Automated setup (recommended)
./setup-dev.sh         # One-time setup of both backend and frontend
./start-dev.sh          # Start both services with hot reload

# Manual setup (if needed)
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Frontend (new terminal)
cd frontend
npm install

# Start services
./start-backend.sh      # Backend only
./start-frontend.sh     # Frontend only
```

### Development Workflow
1. **Initial setup**: Run `./setup-dev.sh` once
2. **Daily development**: Use `./start-dev.sh` to start both services
3. **Backend changes**: Automatic reload on file changes
4. **Frontend changes**: Automatic reload with React dev server
5. **Database**: SQLite file in `./data/` directory (auto-created)

### Project Structure
```
employee-engagement-pulse/
├── 🐍 backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/            # API route definitions
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI application entry
│   ├── requirements.txt    # Python dependencies
│   └── env.template        # Environment configuration template
├── ⚛️ frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API client services
│   │   ├── types/          # TypeScript type definitions
│   │   └── App.tsx         # Main React application
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind CSS configuration
├── 🚀 Setup & Start Scripts:
│   ├── setup-dev.sh        # One-time development setup
│   ├── start-dev.sh        # Start both services (development)
│   ├── start-backend.sh    # Start backend only
│   ├── start-frontend.sh   # Start frontend only
│   ├── build-production.sh # Build for production
│   ├── start-production.sh # Start production server
│   └── verify-setup.sh     # Verify installation and configuration
├── 🐳 Docker files (optional):
│   ├── docker-compose.yml  # Docker orchestration
│   ├── Dockerfile         # Multi-stage container build
│   └── nginx.conf         # Nginx configuration
└── 📖 README.md            # This documentation
```

### Testing
```bash
# Backend tests (if implemented)
cd backend && python -m pytest

# Frontend tests
cd frontend && npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

#### Slack Connection Failed
- Verify bot token starts with `xoxb-`
- Verify app token starts with `xapp-`
- Ensure bot is added to channels you want to monitor
- Check OAuth scopes are correctly configured

#### No Data Appearing
- Confirm monitoring is started in Settings
- Verify channels are added and active
- Check that bot has permission to read channel messages
- Allow time for initial data collection (up to update interval)

#### Docker Issues
```bash
# Reset containers and volumes
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Check logs for specific errors
docker-compose logs engagement-pulse
```

### Getting Help
1. Check the [Issues](../../issues) page for known problems
2. Review Docker logs: `docker-compose logs -f`
3. Verify Slack app configuration matches requirements
4. Ensure environment variables are correctly set

## 🎯 Roadmap

- [ ] **PostgreSQL support** - Production-ready database backend
- [ ] **Multi-workspace support** - Monitor multiple Slack workspaces
- [ ] **Advanced analytics** - Machine learning-based trend prediction
- [ ] **Email notifications** - Automated alerts for managers
- [ ] **Teams/Discord integration** - Support for additional platforms
- [ ] **Mobile dashboard** - Responsive mobile experience
- [ ] **Export capabilities** - PDF reports and data export
- [ ] **Role-based access** - Different permission levels

---

**Made with ❤️ for better team wellbeing and management insights.**
