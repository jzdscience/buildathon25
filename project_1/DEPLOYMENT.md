# Google Cloud Run Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the Screenshot Search application to Google Cloud Run. The app has been configured with all necessary files for containerization and cloud deployment.

## Prerequisites

1. **Google Cloud Account**: You need an active Google Cloud Platform account
2. **Google Cloud Project**: Create or select a project in GCP Console
3. **gcloud CLI**: Install the Google Cloud SDK
   ```bash
   # For Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash
   
   # For macOS
   brew install google-cloud-sdk
   ```
4. **Docker** (optional, for local builds):
   ```bash
   # Install Docker if you want to build locally
   curl -fsSL https://get.docker.com | sh
   ```

## Files Created for Deployment

- `app.py` - Main Flask application configured for Cloud Run
- `Dockerfile` - Full version with AI capabilities
- `Dockerfile.simple` - Lightweight version for demo
- `requirements-simple.txt` - Minimal dependencies for demo
- `.dockerignore` - Optimizes Docker build context
- `cloudbuild.yaml` - Automated build configuration
- `deploy.sh` - Deployment helper script

## Quick Start Deployment

### Option 1: Using the Deployment Script (Recommended)

1. **Set your project ID**:
   ```bash
   export GCP_PROJECT_ID=your-project-id
   export GCP_REGION=us-central1  # Optional, defaults to us-central1
   ```

2. **Make the script executable**:
   ```bash
   chmod +x deploy.sh
   ```

3. **Run the deployment script**:
   ```bash
   ./deploy.sh
   ```

4. **Select deployment method**:
   - Option 1: Cloud Build (recommended)
   - Option 3: Local build with simple version (fastest)
   - Option 4: Direct source deployment

### Option 2: Manual Deployment via Cloud Console

1. **Enable required APIs**:
   ```bash
   gcloud services enable run.googleapis.com \
     cloudbuild.googleapis.com \
     containerregistry.googleapis.com
   ```

2. **Deploy directly from source**:
   ```bash
   gcloud run deploy screenshot-search \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2
   ```

### Option 3: Using Cloud Build

1. **Submit build**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

This will automatically build and deploy your application.

## Deployment Configurations

### Resource Allocation
- **Memory**: 2GB (suitable for image processing)
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds
- **Max Instances**: 10 (auto-scaling)
- **Min Instances**: 0 (scales to zero when idle)

### Environment Variables
The app automatically uses these environment variables:
- `PORT` - Set by Cloud Run (defaults to 8080)
- `SECRET_KEY` - Optional, for Flask sessions
- `UPLOAD_FOLDER` - Directory for uploaded files

## Choosing the Right Version

### Simple Demo Version (Recommended for Testing)
- Uses `Dockerfile.simple` and `requirements-simple.txt`
- No AI dependencies (faster deployment)
- Basic text matching for search
- Smaller container size (~200MB)
- Faster cold starts

### Full Version (With AI Capabilities)
- Uses main `Dockerfile` and `requirements.txt`
- Includes OCR and visual analysis
- Larger container size (~2GB)
- Requires more memory and CPU

## Post-Deployment Steps

1. **Access your application**:
   - The deployment will provide a URL like: `https://screenshot-search-xxxxx-uc.a.run.app`
   - Open this URL in your browser

2. **Test the application**:
   - Upload some test images
   - Try searching with different queries
   - Check the health endpoint: `https://your-app-url/health`

3. **Monitor your application**:
   ```bash
   # View logs
   gcloud run services logs read screenshot-search
   
   # View metrics
   gcloud monitoring dashboards list
   ```

## Cost Optimization Tips

1. **Set maximum instances** to prevent unexpected scaling:
   ```bash
   gcloud run services update screenshot-search --max-instances=5
   ```

2. **Use minimum instances = 0** to scale to zero when not in use

3. **Monitor usage**:
   ```bash
   gcloud run services describe screenshot-search --region=us-central1
   ```

## Updating the Application

To deploy updates:

1. **Make your code changes**

2. **Deploy the update**:
   ```bash
   ./deploy.sh
   # Or manually:
   gcloud run deploy screenshot-search --source .
   ```

## Troubleshooting

### Common Issues and Solutions

1. **"Permission denied" error**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **"APIs not enabled" error**:
   ```bash
   gcloud services enable run.googleapis.com
   ```

3. **Container fails to start**:
   - Check logs: `gcloud run services logs read screenshot-search`
   - Verify PORT environment variable is used
   - Ensure all dependencies are in requirements.txt

4. **Out of memory errors**:
   - Increase memory allocation:
   ```bash
   gcloud run services update screenshot-search --memory=4Gi
   ```

### Debug Commands

```bash
# View service details
gcloud run services describe screenshot-search --region=us-central1

# View recent logs
gcloud run services logs read screenshot-search --limit=50

# List all Cloud Run services
gcloud run services list

# Delete the service (if needed)
gcloud run services delete screenshot-search --region=us-central1
```

## Security Considerations

1. **Authentication**: Currently set to `--allow-unauthenticated` for demo purposes. For production:
   ```bash
   gcloud run services update screenshot-search --no-allow-unauthenticated
   ```

2. **Secrets Management**: Use Google Secret Manager for sensitive data:
   ```bash
   gcloud secrets create app-secret-key --data-file=-
   gcloud run services update screenshot-search \
     --set-secrets=SECRET_KEY=app-secret-key:latest
   ```

3. **File Upload Limits**: The app limits uploads to 16MB per file

## Custom Domain (Optional)

To use a custom domain:

1. **Verify domain ownership** in Google Cloud Console
2. **Map the domain**:
   ```bash
   gcloud run domain-mappings create --service=screenshot-search \
     --domain=your-domain.com --region=us-central1
   ```

## Support and Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Flask on Cloud Run Guide](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/python)
- [Pricing Calculator](https://cloud.google.com/products/calculator)

## Summary

Your Screenshot Search app is now ready for deployment to Google Cloud Run! The configuration provides:

✅ Automatic scaling (0-10 instances)
✅ HTTPS endpoint with Google-managed SSL
✅ Container-based deployment
✅ Pay-per-use pricing (scales to zero)
✅ Global CDN and load balancing
✅ Integrated monitoring and logging

Simply run `./deploy.sh` and choose your preferred deployment method to get started!

