# Deployment Guide for Codebase Time Machine

This guide covers deploying the Codebase Time Machine application using Docker and Google Cloud Run.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Docker Testing](#local-docker-testing)
- [Google Cloud Run Deployment](#google-cloud-run-deployment)
- [Alternative Deployment Methods](#alternative-deployment-methods)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### For Local Docker Testing

- Docker installed on your machine
- Git (for cloning repositories)

### For Google Cloud Run Deployment

- Google Cloud Platform (GCP) account
- Google Cloud SDK (`gcloud`) installed and configured
- A GCP project with billing enabled
- Required APIs enabled:
  - Cloud Run API
  - Cloud Build API
  - Container Registry API

## Local Docker Testing

### 1. Build the Docker Image

```bash
# Navigate to the project directory
cd /path/to/project_4

# Build the Docker image
docker build -t codebase-time-machine:latest .
```

### 2. Run the Container Locally

```bash
# Run with default port 8080
docker run -p 8080:8080 -e PORT=8080 codebase-time-machine:latest

# Or run with a different port
docker run -p 5000:5000 -e PORT=5000 codebase-time-machine:latest
```

### 3. Access the Application

Open your browser and navigate to `http://localhost:8080` (or the port you specified).

## Google Cloud Run Deployment

### Method 1: Using Cloud Build (Recommended)

1. **Set up your GCP project:**

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

2. **Deploy using Cloud Build:**

```bash
# Submit the build and deploy
gcloud builds submit --config cloudbuild.yaml

# Or manually trigger with substitutions
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_REGION=us-central1
```

### Method 2: Manual Deployment

1. **Build and push the Docker image:**

```bash
# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker

# Build the image
docker build -t gcr.io/$PROJECT_ID/codebase-time-machine:latest .

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/codebase-time-machine:latest
```

2. **Deploy to Cloud Run:**

```bash
gcloud run deploy codebase-time-machine \
  --image gcr.io/$PROJECT_ID/codebase-time-machine:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 900 \
  --max-instances 10 \
  --min-instances 0 \
  --port 8080
```

### Method 3: Using Google Cloud Console

1. Navigate to [Cloud Run](https://console.cloud.google.com/run) in the Google Cloud Console
2. Click "Create Service"
3. Select "Deploy one revision from an existing container image"
4. Enter your container image URL: `gcr.io/PROJECT_ID/codebase-time-machine:latest`
5. Configure service settings:
   - Service name: `codebase-time-machine`
   - Region: Select your preferred region
   - CPU allocation: 2 CPU
   - Memory: 2 GiB
   - Request timeout: 900 seconds
   - Maximum instances: 10
   - Minimum instances: 0
6. Under "Authentication", select "Allow unauthenticated invocations"
7. Click "Create"

## Alternative Deployment Methods

### Deploy with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

env:
  PROJECT_ID: your-project-id
  SERVICE: codebase-time-machine
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - uses: google-github-actions/auth@v0
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
      
      - uses: google-github-actions/setup-gcloud@v0
      
      - name: Build and Push
        run: |
          gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE
      
      - name: Deploy
        run: |
          gcloud run deploy $SERVICE \
            --image gcr.io/$PROJECT_ID/$SERVICE \
            --platform managed \
            --region $REGION \
            --allow-unauthenticated
```

### Deploy to Other Cloud Providers

#### AWS ECS/Fargate

1. Build and push to Amazon ECR
2. Create an ECS task definition
3. Deploy as a Fargate service

#### Azure Container Instances

1. Build and push to Azure Container Registry
2. Deploy using Azure Container Instances or Azure App Service

#### Heroku

1. Create a `heroku.yml`:

```yaml
build:
  docker:
    web: Dockerfile
```

2. Deploy:

```bash
heroku create your-app-name
heroku stack:set container
git push heroku main
```

## Configuration

### Environment Variables

The application supports the following environment variables:

- `PORT`: The port to run the application on (required for Cloud Run)
- `DEBUG`: Set to `true` to enable debug mode (default: `false`)
- `PYTHONUNBUFFERED`: Set to `1` for unbuffered output (recommended)

### Resource Requirements

Recommended Cloud Run settings:

- **Memory**: 2 GiB minimum (for repository analysis)
- **CPU**: 2 vCPU minimum
- **Timeout**: 900 seconds (15 minutes) for large repository analysis
- **Max instances**: 10 (adjust based on expected load)
- **Min instances**: 0 (for cost optimization) or 1 (for faster cold starts)

## Monitoring and Logging

### View Logs

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision \
  AND resource.labels.service_name=codebase-time-machine" \
  --limit 50

# Stream logs
gcloud alpha run services logs tail codebase-time-machine \
  --region us-central1
```

### View Metrics

Access metrics in the Google Cloud Console:
1. Navigate to Cloud Run
2. Click on your service
3. View the "Metrics" tab

## Troubleshooting

### Common Issues

1. **Port binding errors:**
   - Ensure the app uses the `PORT` environment variable
   - Cloud Run dynamically assigns ports

2. **Memory issues:**
   - Increase memory allocation for large repository analysis
   - Consider implementing streaming for large datasets

3. **Timeout errors:**
   - Increase the request timeout (max 60 minutes for Cloud Run)
   - Consider implementing background processing for long-running tasks

4. **WebSocket issues:**
   - Cloud Run supports WebSockets with session affinity
   - Ensure client reconnection logic is implemented

5. **Cold start delays:**
   - Set minimum instances to 1
   - Optimize Docker image size
   - Use multi-stage builds

### Debug Locally

```bash
# Run with debug mode enabled
docker run -p 8080:8080 -e PORT=8080 -e DEBUG=true codebase-time-machine:latest

# Check container logs
docker logs <container-id>

# Access container shell
docker exec -it <container-id> /bin/bash
```

### Performance Optimization

1. **Docker Image Optimization:**
   - Use multi-stage builds
   - Minimize layer count
   - Use `.dockerignore` to exclude unnecessary files

2. **Application Optimization:**
   - Implement caching for repository analysis
   - Use CDN for static assets
   - Optimize database queries

3. **Cloud Run Optimization:**
   - Configure appropriate concurrency settings
   - Use Cloud CDN for static content
   - Implement Cloud Memorystore for caching

## Security Considerations

1. **Authentication:**
   - Enable Cloud IAM authentication for production
   - Implement user authentication if needed

2. **Secrets Management:**
   - Use Google Secret Manager for sensitive data
   - Never commit secrets to version control

3. **Network Security:**
   - Use Cloud Armor for DDoS protection
   - Configure VPC connector for private resources

## Cost Optimization

1. **Set maximum instances** to prevent unexpected costs
2. **Use minimum instances = 0** when not in production
3. **Monitor usage** through Cloud Monitoring
4. **Set up budget alerts** in GCP Billing

## Support

For issues or questions:
1. Check the application logs
2. Review this documentation
3. Check Cloud Run quotas and limits
4. Consult Google Cloud Run documentation

## Quick Commands Reference

```bash
# Build locally
docker build -t codebase-time-machine:latest .

# Run locally
docker run -p 8080:8080 -e PORT=8080 codebase-time-machine:latest

# Deploy to Cloud Run (quick)
gcloud run deploy codebase-time-machine \
  --source . \
  --region us-central1 \
  --allow-unauthenticated

# View service URL
gcloud run services describe codebase-time-machine \
  --region us-central1 \
  --format 'value(status.url)'

# Delete service
gcloud run services delete codebase-time-machine --region us-central1
```

