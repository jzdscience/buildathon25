# 🚀 Google Cloud Run Deployment Guide

## Quick Fix for Puppeteer/Chrome Issues

If you're seeing the error about "Failed to launch browser process" or "Permission denied", follow these steps:

### Immediate Solution

```bash
# Use the quick redeploy script with the fixed configuration
./redeploy.sh
```

This will rebuild and redeploy your service with the optimized Dockerfile that fixes the Chrome/Puppeteer permission issues.

## Understanding the Fix

The original error occurred because:
1. Chrome couldn't create necessary directories due to permission issues
2. The non-root user (pptruser) didn't have proper home directory setup
3. Chrome sandbox mode conflicts with Cloud Run's container environment

### What We Fixed:

1. **Updated Dockerfile** (`Dockerfile.cloudrun`):
   - Runs as root for maximum compatibility (Cloud Run handles security)
   - Properly configures Chrome directories
   - Sets up all necessary permissions

2. **Enhanced Puppeteer Configuration**:
   - Added `--no-zygote` and `--single-process` flags for container compatibility
   - Specified user data directory in `/tmp/.chrome`
   - Increased timeout for slower Cloud Run cold starts

3. **Chrome Launch Arguments**:
   ```javascript
   '--no-sandbox',              // Required for containers
   '--disable-setuid-sandbox',  // Bypass sandbox requirements
   '--no-zygote',              // Single process mode
   '--single-process',         // Better for containers
   '--user-data-dir=/tmp/.chrome'  // Writable directory
   ```

## Deployment Options

### Option 1: Automated Deployment (Recommended)
```bash
# This uses the fixed Dockerfile.cloudrun automatically
./redeploy.sh
```

### Option 2: Manual Deployment with Fixed Dockerfile
```bash
# Build with the Cloud Run optimized Dockerfile
docker build -f Dockerfile.cloudrun -t gcr.io/$PROJECT_ID/voice-to-slide-generator .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/voice-to-slide-generator

# Deploy to Cloud Run
gcloud run deploy voice-to-slide-generator \
  --image gcr.io/$PROJECT_ID/voice-to-slide-generator \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --update-secrets OPENAI_API_KEY=openai-api-key:latest
```

### Option 3: Using Cloud Build
```bash
# This automatically uses Dockerfile.cloudrun
gcloud builds submit --config=cloudbuild.yaml
```

## Troubleshooting Common Issues

### 1. Browser Launch Failures
**Error**: `Failed to launch the browser process`

**Solution**: Already fixed in `Dockerfile.cloudrun` and the updated Puppeteer config. Just redeploy.

### 2. Permission Denied Errors
**Error**: `mkdir: cannot create directory '/home/pptruser': Permission denied`

**Solution**: The new Dockerfile runs as root, eliminating permission issues.

### 3. Chrome Crashpad Errors
**Error**: `chrome_crashpad_handler: --database is required`

**Solution**: Added `--disable-web-security` and `--disable-features=IsolateOrigins` flags.

### 4. Timeout Issues
**Error**: `TimeoutError: Timed out after 30000 ms`

**Solution**: Increased Puppeteer launch timeout to 60 seconds in the code.

## Monitoring Your Deployment

### Check Service Status
```bash
gcloud run services describe voice-to-slide-generator \
  --region=us-central1 \
  --format="value(status.url)"
```

### View Recent Logs
```bash
gcloud run services logs read voice-to-slide-generator \
  --region=us-central1 \
  --limit=50
```

### Stream Live Logs
```bash
gcloud run services logs tail voice-to-slide-generator \
  --region=us-central1
```

## Performance Optimization

### Cold Start Mitigation
- Set minimum instances to 1 to avoid cold starts:
  ```bash
  gcloud run services update voice-to-slide-generator \
    --min-instances=1 \
    --region=us-central1
  ```

### Memory and CPU
- Current settings (2Gi RAM, 2 CPUs) are optimal for Chrome
- Don't reduce below these values or Chrome may crash

## Environment Variables

Make sure your OpenAI API key is properly set:

### Update Secret
```bash
echo -n "your-openai-api-key" | gcloud secrets versions add openai-api-key --data-file=-
```

### Verify Secret is Linked
```bash
gcloud run services describe voice-to-slide-generator \
  --region=us-central1 \
  --format="export" | grep OPENAI
```

## Testing After Deployment

1. **Basic Health Check**:
   ```bash
   curl $(gcloud run services describe voice-to-slide-generator \
     --region=us-central1 \
     --format="value(status.url)")
   ```

2. **Test with Sample Audio**:
   - Visit your service URL
   - Upload a small audio file
   - Check logs if it fails:
     ```bash
     gcloud run services logs read voice-to-slide-generator \
       --region=us-central1 \
       --limit=20
     ```

## Cost Management

### View Current Configuration
```bash
gcloud run services describe voice-to-slide-generator \
  --region=us-central1 \
  --format="table(spec.template.spec.containers[0].resources.limits)"
```

### Optimize for Cost
```bash
# Scale to zero when not in use (default)
gcloud run services update voice-to-slide-generator \
  --min-instances=0 \
  --max-instances=10 \
  --region=us-central1
```

## Rolling Back

If you need to rollback to a previous version:

```bash
# List all revisions
gcloud run revisions list \
  --service=voice-to-slide-generator \
  --region=us-central1

# Rollback to specific revision
gcloud run services update-traffic voice-to-slide-generator \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```

## Support

If you continue to experience issues after redeployment:

1. Check the logs for specific error messages
2. Ensure your OpenAI API key is valid and has credits
3. Verify the service has proper IAM permissions
4. Try deploying to a different region if issues persist

---

**Remember**: After any code changes, always use `./redeploy.sh` for the quickest and most reliable deployment with all fixes applied.


