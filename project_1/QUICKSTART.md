# Quick Start - Deploy to Google Cloud Run

## 🚀 Fastest Deployment (Under 5 Minutes)

### Prerequisites
1. Have a Google Cloud account
2. Install gcloud CLI: `curl https://sdk.cloud.google.com | bash`

### Option A: One-Command Deploy (Recommended) ✨

```bash
# Just run this with your project ID:
./deploy-now.sh your-project-id

# Or set environment variable and run:
export GCP_PROJECT_ID=your-project-id
./deploy-now.sh
```

### Option B: Manual Deploy

```bash
# Step 1: Set your project ID
export GCP_PROJECT_ID=your-project-id

# Step 2: Authenticate and set project
gcloud auth login
gcloud config set project $GCP_PROJECT_ID
gcloud services enable run.googleapis.com

# Step 3: Use the optimized Dockerfile
cp Dockerfile.cloudrun Dockerfile

# Step 4: Deploy directly from source
gcloud run deploy screenshot-search \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

That's it! Your app will be live in about 3-5 minutes. 🎉

## 📱 Using the Deployment Script

For more control, use our deployment script:

```bash
# Make executable
chmod +x deploy.sh

# Run it
./deploy.sh
```

Choose option 4 for the fastest deployment (simple version).

## 🔗 After Deployment

Your app will be available at:
```
https://screenshot-search-xxxxx-uc.a.run.app
```

Test it by:
1. Opening the URL in your browser
2. Uploading some screenshots
3. Searching with keywords like "sample", "image", or "text"

## 💰 Cost Information

- **Free Tier**: 2 million requests/month, 360,000 GB-seconds of memory
- **Typical Cost**: $0-5/month for light usage
- **Auto-scales to zero**: No charges when not in use

## 🛠️ Troubleshooting

If deployment fails:

```bash
# Check if you're logged in
gcloud auth list

# Set the correct project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
```

## 📚 Full Documentation

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions and advanced options.

---
**Ready to deploy? Run the commands above and your app will be live on Google Cloud Run!** 🚀
