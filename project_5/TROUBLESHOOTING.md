# Troubleshooting Guide for Cloud Run Deployment

## Common Issues and Solutions

### 1. ImportError: cannot import name 'cached_download' from 'huggingface_hub'

**Problem**: This error occurs due to version incompatibility between `sentence-transformers` and `huggingface_hub`.

**Solution**: 
- Updated `requirements.txt` with compatible versions:
  ```
  sentence-transformers==2.3.1
  huggingface-hub==0.20.1
  transformers==4.38.0
  ```
- Rebuild and redeploy your container

### 2. Model Download Timeout During Container Startup

**Problem**: The container times out while downloading ML models at runtime.

**Solution**: 
- Models are now pre-downloaded during the Docker build process
- The Dockerfile includes:
  ```dockerfile
  RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
  ```

### 3. Memory Errors

**Problem**: Out of memory errors during document processing.

**Symptoms**:
- Container crashes with exit code 137
- "Memory limit exceeded" in logs

**Solutions**:
1. Increase memory allocation:
   ```bash
   gcloud run services update knowledge-graph-builder \
     --memory 4Gi \
     --cpu 4
   ```

2. Optimize document processing:
   - Process documents in smaller batches
   - Limit document size in uploads

### 4. Build Failures

**Problem**: Docker build fails on Cloud Build.

**Common Causes & Solutions**:

a) **Network timeout during package installation**:
   - Add retry logic or use Cloud Build with longer timeout:
   ```yaml
   timeout: '1800s'  # 30 minutes
   ```

b) **Package conflicts**:
   - Ensure all versions in requirements.txt are compatible
   - Test locally first: `docker build -t test .`

### 5. Container Fails to Start

**Problem**: Container builds but fails to start on Cloud Run.

**Check**:
1. Port configuration:
   ```python
   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port)
   ```

2. View logs:
   ```bash
   gcloud run services logs read knowledge-graph-builder --limit 50
   ```

### 6. 502 Bad Gateway Errors

**Problem**: Application returns 502 errors.

**Solutions**:
1. Increase timeout:
   ```bash
   gcloud run services update knowledge-graph-builder --timeout 600
   ```

2. Check if Gunicorn is properly configured:
   ```dockerfile
   CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
   ```

### 7. Slow Cold Starts

**Problem**: First request after idle period is very slow.

**Solutions**:
1. Set minimum instances:
   ```bash
   gcloud run services update knowledge-graph-builder --min-instances 1
   ```

2. Optimize imports - lazy load heavy libraries:
   ```python
   def get_model():
       global _model
       if _model is None:
           from sentence_transformers import SentenceTransformer
           _model = SentenceTransformer('all-MiniLM-L6-v2')
       return _model
   ```

### 8. File Upload Issues

**Problem**: Large file uploads fail.

**Solutions**:
1. Increase request timeout in Cloud Run
2. Use Cloud Storage for large files:
   ```python
   from google.cloud import storage
   # Implement Cloud Storage upload
   ```

3. Increase max request size in Flask:
   ```python
   app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
   ```

## Debugging Commands

### View Service Details
```bash
gcloud run services describe knowledge-graph-builder \
  --region us-central1 \
  --format yaml
```

### Stream Logs
```bash
gcloud run services logs tail knowledge-graph-builder \
  --region us-central1
```

### Check Build History
```bash
gcloud builds list --limit 5
```

### View Build Logs
```bash
gcloud builds log BUILD_ID
```

### Test Container Locally
```bash
# Build
docker build -t test-app .

# Run
docker run -p 8080:8080 -e PORT=8080 test-app

# Test
curl http://localhost:8080
```

### Force Redeploy
```bash
# Update with a new image tag
gcloud builds submit --tag gcr.io/$PROJECT_ID/knowledge-graph-builder:v2

# Deploy new version
gcloud run deploy knowledge-graph-builder \
  --image gcr.io/$PROJECT_ID/knowledge-graph-builder:v2 \
  --region us-central1
```

## Performance Optimization

### 1. Reduce Container Size
- Use multi-stage builds
- Clean pip cache: `pip install --no-cache-dir`
- Remove unnecessary files in .dockerignore

### 2. Optimize Dependencies
- Only install required packages
- Use lighter alternatives where possible
- Pin versions for consistency

### 3. Cache Static Assets
- Use Cloud CDN for static files
- Implement browser caching headers

### 4. Database Connections
- Use connection pooling
- Implement retry logic
- Use Cloud SQL Proxy for Cloud SQL

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError` | Missing dependency | Check requirements.txt |
| `OSError: [Errno 28] No space left on device` | Disk full | Increase disk size or clean temp files |
| `Error: memory limit exceeded` | OOM | Increase memory allocation |
| `Error 503: Service Unavailable` | Container crash | Check logs for errors |
| `Error 504: Gateway Timeout` | Request timeout | Increase timeout setting |
| `Permission denied` | IAM issue | Check service account permissions |

## Getting Help

1. **Check Logs First**:
   ```bash
   gcloud run services logs read knowledge-graph-builder --limit 100
   ```

2. **Enable Debug Logging**:
   Add to your app:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Cloud Run Support**:
   - [Documentation](https://cloud.google.com/run/docs)
   - [Troubleshooting Guide](https://cloud.google.com/run/docs/troubleshooting)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-run)

4. **Community**:
   - Google Cloud Community
   - GitHub Issues
   - Stack Overflow

## Rollback Procedure

If deployment fails:

1. **List revisions**:
   ```bash
   gcloud run revisions list --service knowledge-graph-builder
   ```

2. **Rollback to previous revision**:
   ```bash
   gcloud run services update-traffic knowledge-graph-builder \
     --to-revisions PREVIOUS_REVISION_NAME=100
   ```

3. **Or redeploy last known good image**:
   ```bash
   gcloud run deploy knowledge-graph-builder \
     --image gcr.io/$PROJECT_ID/knowledge-graph-builder:last-good-tag
   ```

