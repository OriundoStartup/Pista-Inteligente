---
description: Deploy to Vercel (Frontend)
---

# Deploy to Vercel

This workflow outlines the deployment process for the frontend application to Vercel.

## Prerequisites
- Vercel CLI installed (optional, for manual deploys)
- Git repository connected to Vercel project `pista-inteligente`

## Automatic Deployment
The primary deployment method is via Git Push.

### 1. Push changes to main branch
// turbo
```bash
git push origin main
```
This will automatically trigger a new deployment on Vercel.

## Manual Deployment (CLI)
If you need to deploy manually from your local machine:

### 1. Deploy to Preview
```bash
cd frontend
vercel
```

### 2. Deploy to Production
```bash
cd frontend
vercel --prod
```

## Configuration Notes
- The project root for Vercel is set to `./frontend` (implied by structure).
- Use `.vercelignore` to exclude backend files from the build context.
