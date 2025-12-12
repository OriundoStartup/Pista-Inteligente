---
description: Deploy to Cloud Run with optimized settings for low latency
---

# Deploy to Cloud Run (Optimized)

This workflow deploys the application to Cloud Run with optimized settings for minimal cold starts and low latency.

## Prerequisites
- Google Cloud CLI installed and authenticated
- Docker installed
- Project configured: `pista-inteligente`

## Steps

### 1. Build Docker Image
// turbo
```bash
docker build -t gcr.io/pista-inteligente/pista-inteligente-metrics .
```

### 2. Push to Container Registry
// turbo
```bash
docker push gcr.io/pista-inteligente/pista-inteligente-metrics
```

### 3. Deploy to Cloud Run with Optimized Settings
```bash
gcloud run deploy pista-inteligente-metrics \
  --image gcr.io/pista-inteligente/pista-inteligente-metrics \
  --region us-central1 \
  --platform managed \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 80 \
  --timeout 300 \
  --cpu-boost \
  --no-cpu-throttling \
  --allow-unauthenticated
```

### 4. Deploy Firebase Hosting (Static Assets to CDN)
// turbo
```bash
firebase deploy --only hosting
```

## Configuration Options Explained

| Option | Value | Purpose |
|--------|-------|---------|
| `--min-instances 1` | 1 | Keeps 1 instance always warm - eliminates cold starts |
| `--no-cpu-throttling` | - | CPU always allocated, not just during requests |
| `--cpu-boost` | - | Extra CPU during startup for faster initialization |
| `--concurrency 80` | 80 | Requests handled per instance |
| `--memory 1Gi` | 1GB | Sufficient for ML model + data |

## Cost Considerations

With `--min-instances 1`, you pay for 1 always-on instance (~$0.00002400/vCPU-second).
Monthly estimate: ~$15-25 USD for 1 min instance.

To save costs during development, set `--min-instances 0`.
