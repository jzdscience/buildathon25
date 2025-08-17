# Google Cloud Run Deployment Guide

This guide explains how to deploy the Universal Knowledge-Graph Builder to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account**: Create a free account at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud Project**: Create a new project or use an existing one
3. **Enable Required APIs**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```
4. **Install Google Cloud SDK**: Follow the [installation guide](https://cloud.google.com/sdk/docs/install)
5. **Docker** (optional, for local builds): Install from [docker.com](https://www.docker.com/get-started)

## Quick Deployment

### Option 1: Automated Deployment Script (Recommended)

```bash
# Make the script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

The script will guide you through the deployment process and offer two options:
- Use Google Cloud Build (recommended)
- Build locally and push to Container Registry

### Option 2: Manual Deployment with Cloud Build

1. **Set your project ID**:
   ```bash
   export PROJECT_ID=your-project-id
   gcloud config set project $PROJECT_ID
   ```

2. **Submit to Cloud Build**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

3. **Wait for deployment to complete** (typically 5-10 minutes)

### Option 3: Manual Local Build and Deploy

1. **Build the Docker image**:
   ```bash
   docker build -t gcr.io/$PROJECT_ID/knowledge-graph-builder:latest .
   ```

2. **Configure Docker authentication**:
   ```bash
   gcloud auth configure-docker
   ```

3. **Push the image to Container Registry**:
   ```bash
   docker push gcr.io/$PROJECT_ID/knowledge-graph-builder:latest
   ```

4. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy knowledge-graph-builder \
     --image gcr.io/$PROJECT_ID/knowledge-graph-builder:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2 \
     --timeout 300 \
     --max-instances 10 \
     --port 8080
   ```

## Configuration Options

### Resource Allocation

The default configuration uses:
- **Memory**: 2 GiB (suitable for moderate workloads)
- **CPU**: 2 vCPUs
- **Timeout**: 300 seconds (5 minutes)
- **Max Instances**: 10 (auto-scaling)
- **Min Instances**: 0 (scale to zero when idle)

To adjust resources:
```bash
gcloud run services update knowledge-graph-builder \
  --memory 4Gi \
  --cpu 4 \
  --max-instances 20
```

### Environment Variables

Add environment variables if needed:
```bash
gcloud run services update knowledge-graph-builder \
  --set-env-vars KEY1=value1,KEY2=value2
```

### Authentication

By default, the service is publicly accessible. To require authentication:
```bash
gcloud run services update knowledge-graph-builder \
  --no-allow-unauthenticated
```

## Testing Your Deployment

1. **Get the service URL**:
   ```bash
   gcloud run services describe knowledge-graph-builder \
     --region us-central1 \
     --format 'value(status.url)'
   ```

2. **Visit the URL in your browser** to access the application

3. **Test the API endpoints**:
   ```bash
   # Upload and process documents
   curl -X POST https://your-service-url/upload \
     -F "files=@example_documents/ai.txt"
   
   # Get statistics
   curl https://your-service-url/statistics
   ```

## Monitoring and Logs

### View Logs
```bash
# Stream logs in real-time
gcloud run services logs tail knowledge-graph-builder

# Read recent logs
gcloud run services logs read knowledge-graph-builder --limit 50
```

### Monitor Metrics
Visit the [Cloud Run Console](https://console.cloud.google.com/run) to view:
- Request count and latency
- CPU and memory usage
- Error rates
- Auto-scaling metrics

## Cost Optimization

Cloud Run charges only for resources used during request processing:

1. **Scale to Zero**: The service automatically scales to zero when not in use (no charges)
2. **Request-based Billing**: You pay only for the compute time used to handle requests
3. **Free Tier**: Cloud Run offers a generous free tier:
   - 2 million requests per month
   - 360,000 GB-seconds of memory
   - 180,000 vCPU-seconds

### Cost Saving Tips

- Set appropriate memory limits (avoid over-provisioning)
- Configure max instances to prevent unexpected scaling
- Use Cloud CDN for static assets if traffic increases
- Enable CPU allocation only during request processing:
  ```bash
  gcloud run services update knowledge-graph-builder \
    --cpu-throttling
  ```

## Troubleshooting

### Common Issues

1. **Build Fails**
   - Check Cloud Build logs: `gcloud builds list --limit 5`
   - Ensure all APIs are enabled
   - Verify Docker configuration

2. **Deployment Fails**
   - Check service logs for errors
   - Verify resource limits are sufficient
   - Ensure the PORT environment variable is used correctly

3. **Application Errors**
   - Check application logs for Python errors
   - Verify all dependencies are installed
   - Test locally with Docker first:
     ```bash
     docker build -t test-app .
     docker run -p 8080:8080 -e PORT=8080 test-app
     ```

4. **Memory Issues**
   - Increase memory allocation
   - Optimize document processing for large files
   - Consider using Cloud Storage for file uploads

## Advanced Configuration

### Using Cloud Storage for Uploads

For production, consider using Cloud Storage instead of local file uploads:

1. Create a storage bucket:
   ```bash
   gsutil mb gs://$PROJECT_ID-uploads
   ```

2. Update the application to use Cloud Storage (requires code changes)

3. Grant service account permissions:
   ```bash
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/storage.objectAdmin"
   ```

### Custom Domain

Add a custom domain to your Cloud Run service:

1. Verify domain ownership in Google Search Console
2. Map the domain:
   ```bash
   gcloud run domain-mappings create \
     --service knowledge-graph-builder \
     --domain your-domain.com \
     --region us-central1
   ```

### CI/CD Integration

#### GitHub Actions
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      - run: gcloud builds submit --config cloudbuild.yaml
```

#### GitLab CI
Add to `.gitlab-ci.yml`:
```yaml
deploy:
  stage: deploy
  image: google/cloud-sdk:latest
  script:
    - echo $GCP_SERVICE_KEY > gcloud-service-key.json
    - gcloud auth activate-service-account --key-file gcloud-service-key.json
    - gcloud config set project $GCP_PROJECT_ID
    - gcloud builds submit --config cloudbuild.yaml
  only:
    - main
```

## Security Best Practices

1. **Use Secret Manager** for sensitive data:
   ```bash
   echo -n "your-secret" | gcloud secrets create my-secret --data-file=-
   gcloud run services update knowledge-graph-builder \
     --set-secrets=SECRET_KEY=my-secret:latest
   ```

2. **Enable VPC Connector** for private resources:
   ```bash
   gcloud run services update knowledge-graph-builder \
     --vpc-connector=my-connector
   ```

3. **Set up Cloud Armor** for DDoS protection (requires Load Balancer)

4. **Regular Updates**: Keep dependencies updated and rebuild regularly

## Cleanup

To avoid charges when not using the service:

```bash
# Delete the Cloud Run service
gcloud run services delete knowledge-graph-builder --region us-central1

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/knowledge-graph-builder

# Disable APIs (optional)
gcloud services disable run.googleapis.com
gcloud services disable cloudbuild.googleapis.com
```

## Support and Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Pricing Calculator](https://cloud.google.com/products/calculator)
- [Stack Overflow - Google Cloud Run](https://stackoverflow.com/questions/tagged/google-cloud-run)

## Next Steps

1. Set up monitoring and alerting
2. Configure automated backups for graph data
3. Implement caching with Cloud CDN
4. Add Cloud Firestore for persistent storage
5. Set up Cloud Scheduler for periodic tasks

