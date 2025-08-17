# Google Cloud Run Deployment Guide

This guide explains how to deploy the Inbox Triage Assistant to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: You need a Google Cloud account with billing enabled
2. **Google Cloud CLI**: Install the gcloud CLI tool
   ```bash
   # For Linux/Mac:
   curl https://sdk.cloud.google.com | bash
   
   # For Windows: Download installer from
   # https://cloud.google.com/sdk/docs/install
   ```

3. **Docker** (optional): For local testing
   ```bash
   # Test locally with Docker
   docker build -t inbox-triage-assistant .
   docker run -p 8080:8080 inbox-triage-assistant
   ```

## Setup Google Cloud Project

1. **Create a new project or select existing one**:
   ```bash
   # Create new project
   gcloud projects create YOUR-PROJECT-ID --name="Inbox Triage Assistant"
   
   # Or list and select existing project
   gcloud projects list
   gcloud config set project YOUR-PROJECT-ID
   ```

2. **Enable required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Configure authentication**:
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

## Deployment Options

### Option 1: Deploy from Source Code (Recommended)

This is the simplest method - Google Cloud Build will build and deploy automatically:

```bash
# Deploy directly from source
gcloud run deploy inbox-triage-assistant \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="PORT=8080"
```

### Option 2: Deploy with Cloud Build (CI/CD)

Use the included `cloudbuild.yaml` for automated builds:

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml .

# The cloudbuild.yaml will automatically:
# 1. Build the Docker image
# 2. Push to Container Registry
# 3. Deploy to Cloud Run
```

### Option 3: Manual Docker Build and Deploy

Build and push the image manually:

```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Build the Docker image
docker build -t gcr.io/$PROJECT_ID/inbox-triage-assistant .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/inbox-triage-assistant

# Deploy to Cloud Run
gcloud run deploy inbox-triage-assistant \
  --image gcr.io/$PROJECT_ID/inbox-triage-assistant \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

## Environment Variables

### Required for OAuth (Optional Feature)

If you want to enable Google OAuth login:

```bash
gcloud run services update inbox-triage-assistant \
  --set-env-vars="GOOGLE_CLIENT_ID=your-client-id,GOOGLE_CLIENT_SECRET=your-client-secret,SECRET_KEY=your-secret-key" \
  --region us-central1
```

### Production Settings

```bash
# Set production environment variables
gcloud run services update inbox-triage-assistant \
  --set-env-vars="FLASK_DEBUG=False,PORT=8080,SECRET_KEY=$(openssl rand -hex 32)" \
  --region us-central1
```

## Custom Domain (Optional)

To use a custom domain:

```bash
# Map custom domain
gcloud run domain-mappings create \
  --service inbox-triage-assistant \
  --domain your-domain.com \
  --region us-central1
```

## Continuous Deployment with GitHub

1. **Connect GitHub repository**:
   ```bash
   # In Google Cloud Console, go to Cloud Build > Triggers
   # Click "Connect Repository" and follow the steps
   ```

2. **Create build trigger**:
   ```bash
   gcloud builds triggers create github \
     --repo-name=your-repo-name \
     --repo-owner=your-github-username \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

## Monitoring and Logs

View application logs:
```bash
# View recent logs
gcloud run services logs read inbox-triage-assistant --region us-central1

# Stream logs in real-time
gcloud run services logs tail inbox-triage-assistant --region us-central1
```

Check service status:
```bash
# Get service details
gcloud run services describe inbox-triage-assistant --region us-central1

# List all revisions
gcloud run revisions list --service inbox-triage-assistant --region us-central1
```

## Cost Optimization

Cloud Run charges only for actual usage:

- **Scale to Zero**: Set `--min-instances=0` to avoid charges when not in use
- **Memory**: Start with 512Mi and increase only if needed
- **CPU**: 1 CPU is sufficient for most workloads
- **Concurrency**: Default is 1000 concurrent requests per instance

Monitor costs:
```bash
# View current month's costs
gcloud billing accounts list
gcloud alpha billing budgets list
```

## Troubleshooting

### Common Issues

1. **Port binding error**:
   - Ensure the app listens on PORT environment variable
   - Cloud Run sets PORT=8080 by default

2. **Memory issues**:
   ```bash
   # Increase memory if needed
   gcloud run services update inbox-triage-assistant \
     --memory 1Gi \
     --region us-central1
   ```

3. **Timeout errors**:
   ```bash
   # Increase timeout (default is 60s, max is 3600s)
   gcloud run services update inbox-triage-assistant \
     --timeout 300 \
     --region us-central1
   ```

4. **Cold start issues**:
   ```bash
   # Keep minimum instances warm
   gcloud run services update inbox-triage-assistant \
     --min-instances 1 \
     --region us-central1
   ```

### Debug Container Locally

```bash
# Build and run locally
docker build -t inbox-triage-assistant .
docker run -p 8080:8080 -e PORT=8080 inbox-triage-assistant

# Access at http://localhost:8080
```

## Security Best Practices

1. **Authentication**: For private deployments:
   ```bash
   # Remove --allow-unauthenticated flag
   gcloud run deploy inbox-triage-assistant \
     --no-allow-unauthenticated \
     --region us-central1
   ```

2. **Secrets Management**: Use Secret Manager for sensitive data:
   ```bash
   # Create secret
   echo -n "your-secret-value" | gcloud secrets create app-secret-key --data-file=-
   
   # Grant access to Cloud Run service
   gcloud secrets add-iam-policy-binding app-secret-key \
     --member="serviceAccount:YOUR-SERVICE-ACCOUNT" \
     --role="roles/secretmanager.secretAccessor"
   
   # Use in Cloud Run
   gcloud run services update inbox-triage-assistant \
     --set-secrets="SECRET_KEY=app-secret-key:latest" \
     --region us-central1
   ```

3. **VPC Connector**: For private resources:
   ```bash
   # Create VPC connector
   gcloud compute networks vpc-access connectors create my-connector \
     --region us-central1 \
     --subnet my-subnet
   
   # Attach to Cloud Run service
   gcloud run services update inbox-triage-assistant \
     --vpc-connector my-connector \
     --region us-central1
   ```

## Rollback

If deployment fails, rollback to previous version:

```bash
# List all revisions
gcloud run revisions list --service inbox-triage-assistant --region us-central1

# Rollback to specific revision
gcloud run services update-traffic inbox-triage-assistant \
  --to-revisions=REVISION-NAME=100 \
  --region us-central1
```

## Clean Up

To avoid charges, delete resources when not needed:

```bash
# Delete Cloud Run service
gcloud run services delete inbox-triage-assistant --region us-central1

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/inbox-triage-assistant

# Delete the project (removes everything)
gcloud projects delete YOUR-PROJECT-ID
```

## Support

For issues specific to this application:
- Check the application logs in Cloud Run
- Ensure Gmail App Password is correctly configured
- Verify IMAP is enabled in Gmail settings

For Google Cloud Run issues:
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)

