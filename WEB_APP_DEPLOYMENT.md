# 🌐 Web App Deployment Roadmap

Deployment plan for Creative Cloner web application with minimal effort using free services.

---

## 📋 Table of Contents

1. [Recommended Stack](#recommended-stack)
2. [Architecture Overview](#architecture-overview)
3. [Service Setup Steps](#service-setup-steps)
4. [Implementation Phases](#implementation-phases)
5. [File Structure](#file-structure)
6. [Cost Analysis](#cost-analysis)
7. [Deployment Checklist](#deployment-checklist)

---

## 🎯 Recommended Stack

### Primary Stack (Minimal Migration)

| Component | Service | Why | Free Tier |
|-----------|---------|-----|-----------|
| **Frontend** | Vercel | Auto-deploy from GitHub, perfect for Next.js | 100GB bandwidth, unlimited sites |
| **Database** | Airtable | Already set up, zero migration | Unlimited bases, API included |
| **File Storage** | Cloudinary | 25GB free, video optimization, CDN | 25GB storage, 25K transformations |
| **Python Runtime** | Modal | Built for Python, handles long jobs, FFmpeg included | $30/month free credits |
| **API Layer** | Vercel API Routes | Serverless, easy integration | Included with Vercel |

### Alternative Options

**If migrating database:**
- Supabase (PostgreSQL + Storage + Auth all-in-one)
- Firebase (Google ecosystem, good docs)
- PlanetScale (MySQL, serverless)

**For Python runtime:**
- Railway (good for web servers, $5/month free)
- Render (750 hours/month free)
- Fly.io (limited free tier)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER BROWSER                         │
│                     (React/Next.js UI)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                    VERCEL (Frontend Host)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  pages/      │  │  API Routes  │  │  components/ │     │
│  │  index.js    │→ │  /api/*      │  │  UI pieces   │     │
│  └──────────────┘  └──────┬───────┘  └──────────────┘     │
└─────────────────────────────┼──────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    MODAL (Python Runtime)                    │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  @stub.function  │  │  @stub.function  │               │
│  │  analyze_video() │  │  generate_imgs() │               │
│  └────────┬─────────┘  └────────┬─────────┘               │
│           │                     │                           │
│           ↓                     ↓                           │
│  ┌──────────────────────────────────────────┐              │
│  │  Uses: Gemini API, Kie.ai API, FFmpeg   │              │
│  └──────────────────┬───────────────────────┘              │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      ↓
          ┌───────────────────────┐
          │                       │
          ↓                       ↓
┌──────────────────┐    ┌──────────────────┐
│    AIRTABLE      │    │   CLOUDINARY     │
│   (Database)     │    │  (File Storage)  │
│                  │    │                  │
│ - Scenes         │    │ - Videos         │
│ - Prompts        │    │ - Images         │
│ - Project data   │    │ - Final outputs  │
└──────────────────┘    └──────────────────┘
```

### Data Flow

1. **User uploads video** → Frontend uploads to Cloudinary
2. **Frontend triggers API** → Vercel API Route called
3. **API calls Modal function** → Python script executes
4. **Modal runs workflow:**
   - Analyze video with Gemini
   - Generate prompts with Gemini
   - Store data in Airtable
   - Generate images with Kie.ai
   - Generate videos with Kie.ai
   - Combine with FFmpeg
   - Upload results to Cloudinary
5. **Frontend polls status** → Check Airtable for progress
6. **User downloads result** → From Cloudinary CDN

---

## 🚀 Service Setup Steps

### 1. Vercel Setup (5 minutes)

**Create account:**
```
https://vercel.com/signup
```

**Install CLI:**
```bash
npm install -g vercel
vercel login
```

**Connect GitHub:**
- Link your GitHub account
- Auto-deploy on push to main

**Environment variables:**
```
AIRTABLE_API_TOKEN=...
AIRTABLE_BASE_ID=...
MODAL_TOKEN=...
CLOUDINARY_URL=...
GEMINI_API_KEY=...
KIE_API_KEY=...
```

---

### 2. Modal Setup (10 minutes)

**Create account:**
```
https://modal.com/signup
```

**Install CLI:**
```bash
pip install modal
modal token new
```

**Create secrets:**
```bash
modal secret create creative-cloner-secrets \
  GEMINI_API_KEY=your_key \
  KIE_API_KEY=your_key \
  AIRTABLE_API_TOKEN=your_token \
  AIRTABLE_BASE_ID=your_base_id
```

**Deploy Python functions:**
```bash
modal deploy modal_app.py
```

---

### 3. Cloudinary Setup (5 minutes)

**Create account:**
```
https://cloudinary.com/users/register/free
```

**Get credentials:**
- Dashboard → Account Details
- Copy: Cloud Name, API Key, API Secret

**Create upload preset:**
- Settings → Upload → Add upload preset
- Name: `creative-cloner-videos`
- Signing Mode: Unsigned
- Folder: `creative-cloner/`

**Environment variable:**
```
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

---

### 4. Airtable (Already Done!)

**Current setup:**
- ✅ Base already created
- ✅ Table schema defined
- ✅ API token exists

**No changes needed** - just use existing credentials!

---

## 📦 Implementation Phases

### Phase 1: Project Setup (30 minutes)

**Create Next.js app:**
```bash
npx create-next-app@latest creative-cloner-web --typescript --tailwind --app
cd creative-cloner-web
```

**Install dependencies:**
```bash
npm install @cloudinary/url-gen cloudinary airtable axios
npm install -D @types/node
```

**Project structure:**
```
creative-cloner-web/
├── app/
│   ├── page.tsx              # Home/Upload page
│   ├── projects/
│   │   └── page.tsx          # View all projects
│   ├── project/
│   │   └── [id]/
│   │       └── page.tsx      # Single project view
│   └── api/
│       ├── upload/
│       │   └── route.ts      # Handle video upload
│       ├── analyze/
│       │   └── route.ts      # Trigger analysis
│       ├── generate/
│       │   └── route.ts      # Trigger generation
│       └── status/
│           └── route.ts      # Check job status
├── components/
│   ├── VideoUpload.tsx       # Upload UI
│   ├── ProgressTracker.tsx   # Show workflow progress
│   ├── ScenePreview.tsx      # Preview scenes
│   └── ResultsView.tsx       # Show final video
├── lib/
│   ├── airtable.ts           # Airtable client
│   ├── cloudinary.ts         # Cloudinary helpers
│   └── modal.ts              # Modal API client
└── public/
    └── ...
```

---

### Phase 2: Modal Functions (2 hours)

**File:** `modal_app.py` (in project root)

```python
import modal
import os
from pathlib import Path

# Create Modal stub
stub = modal.Stub("creative-cloner")

# Define container image with all dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(
        "google-genai>=0.3.0",
        "python-dotenv>=1.0.0",
        "pyyaml>=6.0",
        "pyairtable>=2.3.0",
        "requests>=2.28.0"
    )
    .apt_install("ffmpeg")
)

@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("creative-cloner-secrets")],
    timeout=600  # 10 minutes
)
def analyze_video(video_url: str, project_name: str):
    """Analyze video and extract scenes"""
    # Import your existing code
    import sys
    sys.path.append(str(Path(__file__).parent / "tools"))

    from analyze_video import analyze
    result = analyze(video_url)

    # Save to Airtable
    from log_to_airtable import log_scenes
    log_scenes(result, project_name)

    return result


@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("creative-cloner-secrets")],
    timeout=300  # 5 minutes
)
def generate_prompts(scenes: list, project_name: str):
    """Generate image and video prompts for scenes"""
    import sys
    sys.path.append(str(Path(__file__).parent / "tools"))

    from generate_prompts import generate
    result = generate(scenes)

    # Update Airtable
    from pyairtable import Api
    api = Api(os.getenv('AIRTABLE_API_TOKEN'))
    table = api.table(os.getenv('AIRTABLE_BASE_ID'), 'Scenes')

    for scene in result['scenes']:
        # Find and update record
        records = table.all(formula=f"AND({{project_name}}='{project_name}', {{scene_number}}={scene['scene_number']})")
        if records:
            table.update(records[0]['id'], {
                'image_prompt': scene['image_prompt'],
                'video_prompt': scene['video_prompt']
            })

    return result


@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("creative-cloner-secrets")],
    timeout=1800  # 30 minutes
)
def generate_images(project_name: str, model: str = "nano-banana-pro"):
    """Generate images for all scenes"""
    import sys
    sys.path.append(str(Path(__file__).parent / "tools"))

    from generate_images import generate
    result = generate(project_name, model)

    return result


@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("creative-cloner-secrets")],
    timeout=3600  # 60 minutes (videos take longer)
)
def generate_videos(project_name: str, duration: int = 10):
    """Generate videos from images"""
    import sys
    sys.path.append(str(Path(__file__).parent / "tools"))

    from generate_videos import generate
    result = generate(project_name, duration)

    return result


@stub.function(
    image=image,
    secrets=[modal.Secret.from_name("creative-cloner-secrets")],
    timeout=600
)
def combine_videos(project_name: str, music_url: str = None):
    """Combine all scene videos into final output"""
    import sys
    sys.path.append(str(Path(__file__).parent / "tools"))

    from combine_all import combine
    result = combine(project_name, music_url)

    return result
```

**Deploy:**
```bash
modal deploy modal_app.py
```

---

### Phase 3: Frontend Components (3 hours)

**File:** `app/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import VideoUpload from '@/components/VideoUpload';
import ProgressTracker from '@/components/ProgressTracker';

export default function Home() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle');

  const handleUploadComplete = async (videoUrl: string, projectName: string) => {
    setStatus('analyzing');

    // Trigger analysis
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ videoUrl, projectName })
    });

    const { projectId } = await res.json();
    setProjectId(projectId);
    setStatus('complete');
  };

  return (
    <main className="container mx-auto p-8">
      <h1 className="text-4xl font-bold mb-8">Creative Cloner</h1>

      {!projectId ? (
        <VideoUpload onComplete={handleUploadComplete} />
      ) : (
        <ProgressTracker projectId={projectId} status={status} />
      )}
    </main>
  );
}
```

**File:** `app/api/analyze/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { videoUrl, projectName } = await request.json();

  // Call Modal function
  const modalResponse = await fetch(
    `https://your-modal-workspace--creative-cloner-analyze-video.modal.run`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.MODAL_TOKEN}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ video_url: videoUrl, project_name: projectName })
    }
  );

  const result = await modalResponse.json();

  return NextResponse.json({
    success: true,
    projectId: projectName,
    scenes: result
  });
}
```

---

### Phase 4: API Routes (2 hours)

Create API routes for:
- ✅ `/api/upload` - Handle video upload to Cloudinary
- ✅ `/api/analyze` - Trigger video analysis
- ✅ `/api/generate` - Trigger image/video generation
- ✅ `/api/combine` - Trigger final video combination
- ✅ `/api/status` - Check progress from Airtable

---

### Phase 5: Deploy to Vercel (30 minutes)

**Initialize Git:**
```bash
git init
git add .
git commit -m "Initial web app"
```

**Push to GitHub:**
```bash
gh repo create creative-cloner-web --public
git remote add origin https://github.com/YOUR_USERNAME/creative-cloner-web.git
git push -u origin main
```

**Deploy:**
```bash
vercel --prod
```

**Set environment variables in Vercel dashboard:**
- AIRTABLE_API_TOKEN
- AIRTABLE_BASE_ID
- MODAL_TOKEN
- CLOUDINARY_URL
- GEMINI_API_KEY
- KIE_API_KEY

---

## 📁 File Structure

```
creative-cloner-web/
├── app/
│   ├── page.tsx                    # Home page with upload
│   ├── layout.tsx                  # Root layout
│   ├── globals.css                 # Global styles
│   ├── projects/
│   │   └── page.tsx                # All projects list
│   ├── project/
│   │   └── [id]/
│   │       └── page.tsx            # Single project detail
│   └── api/
│       ├── upload/route.ts         # Upload to Cloudinary
│       ├── analyze/route.ts        # Trigger analysis (Modal)
│       ├── generate-images/route.ts
│       ├── generate-videos/route.ts
│       ├── combine/route.ts
│       └── status/[projectId]/route.ts
│
├── components/
│   ├── VideoUpload.tsx             # Drag-drop upload
│   ├── ProgressTracker.tsx         # Workflow status
│   ├── SceneCard.tsx               # Scene preview
│   ├── CostEstimator.tsx           # Show costs before action
│   └── ResultsView.tsx             # Final video player
│
├── lib/
│   ├── airtable.ts                 # Airtable helpers
│   ├── cloudinary.ts               # Upload helpers
│   ├── modal.ts                    # Modal API client
│   └── types.ts                    # TypeScript types
│
├── modal_app.py                    # Python functions (Modal)
├── tools/                          # Existing Python scripts
│   ├── analyze_video.py
│   ├── generate_prompts.py
│   ├── generate_images.py
│   ├── generate_videos.py
│   └── combine_all.py
│
├── .env.local                      # Local development env
├── .env.example                    # Template for env vars
├── next.config.js
├── package.json
├── tsconfig.json
└── README.md
```

---

## 💰 Cost Analysis

### Free Tier Limits

| Service | Free Tier | What You Get | When You'd Exceed |
|---------|-----------|--------------|-------------------|
| **Vercel** | 100GB bandwidth | ~1000 video downloads/month | Viral growth |
| **Airtable** | 1,200 records/base | ~200 projects (6 scenes each) | Heavy usage |
| **Cloudinary** | 25GB storage | ~250 final videos (100MB each) | After 250 projects |
| **Modal** | $30 credits/month | ~60 complete workflows | After 60 projects |

### Cost Per Project (After Free Tier)

| Operation | Service | Cost | Notes |
|-----------|---------|------|-------|
| Video analysis | Gemini | ~$0.01 | Very cheap |
| Prompt generation | Gemini | ~$0.01 | Very cheap |
| Image generation | Kie.ai | $0.09-$0.18 | 2 scenes @ $0.09 each |
| Video generation | Kie.ai | $1.00 | 2 scenes @ $0.50 each |
| Video combination | FFmpeg | $0.00 | Free (local) |
| Storage | Cloudinary | $0.00 | Free tier |
| **Total** | | **~$1.20** | Per 2-scene project |

### When to Upgrade

**Vercel Pro ($20/month):**
- You exceed 100GB bandwidth
- Need team collaboration
- Want analytics

**Cloudinary Plus ($99/month):**
- Exceed 25GB storage
- Need more transformations
- Want better video quality

**Modal Pay-as-you-go:**
- Automatically charged after $30 credits
- $0.000250/second of compute
- ~$0.50 per video generation

---

## ✅ Deployment Checklist

### Pre-Deployment

- [ ] All Python scripts tested locally
- [ ] Airtable schema finalized
- [ ] API keys obtained (Gemini, Kie.ai, Airtable)
- [ ] Cost limits understood

### Service Setup

- [ ] Vercel account created
- [ ] Modal account created + CLI installed
- [ ] Cloudinary account created
- [ ] GitHub repository created

### Code Setup

- [ ] Next.js app created
- [ ] Modal functions written (`modal_app.py`)
- [ ] API routes implemented
- [ ] Frontend components built
- [ ] Environment variables configured

### Testing

- [ ] Upload video works
- [ ] Analysis completes successfully
- [ ] Images generate correctly
- [ ] Videos generate correctly
- [ ] Final combination works
- [ ] Error handling tested

### Deployment

- [ ] Push to GitHub
- [ ] Connect Vercel to GitHub
- [ ] Set environment variables in Vercel
- [ ] Deploy Modal functions
- [ ] Test production deployment
- [ ] Monitor costs and usage

### Post-Deployment

- [ ] Add custom domain (optional)
- [ ] Set up monitoring (Vercel Analytics)
- [ ] Add error tracking (Sentry)
- [ ] Document API for users
- [ ] Create user guide

---

## 🔧 Environment Variables Reference

### Required for Vercel

```env
# Airtable
AIRTABLE_API_TOKEN=patXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXX

# Modal
MODAL_TOKEN=ak-XXXXXXXXXXXXXXXX
MODAL_WORKSPACE=your-workspace-name

# Cloudinary
CLOUDINARY_URL=cloudinary://key:secret@cloud
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# AI APIs (if calling directly from Next.js)
GEMINI_API_KEY=your-gemini-key
KIE_API_KEY=your-kie-key

# Optional
NEXT_PUBLIC_APP_URL=https://your-app.vercel.app
```

### Required for Modal

```bash
# Create with: modal secret create creative-cloner-secrets
GEMINI_API_KEY=your-gemini-key
KIE_API_KEY=your-kie-key
AIRTABLE_API_TOKEN=patXXXXXXXXXXXXX
AIRTABLE_BASE_ID=appXXXXXXXXXXXXX
```

---

## 🚨 Common Issues & Solutions

### Issue: Modal function timeout

**Problem:** Video generation takes too long
**Solution:** Increase timeout in `@stub.function(timeout=3600)`

### Issue: Cloudinary upload fails

**Problem:** Video too large
**Solution:**
- Implement chunked upload
- Or limit video length on frontend

### Issue: Airtable rate limit

**Problem:** Too many API calls
**Solution:**
- Implement caching
- Batch updates
- Use Airtable's batch API

### Issue: High Modal costs

**Problem:** Exceeding free tier
**Solution:**
- Implement job queue
- Batch processing
- User limits per day

---

## 📚 Additional Resources

### Documentation

- **Vercel:** https://vercel.com/docs
- **Modal:** https://modal.com/docs
- **Cloudinary:** https://cloudinary.com/documentation
- **Airtable API:** https://airtable.com/developers/web/api/introduction
- **Next.js:** https://nextjs.org/docs

### Tutorials

- **Next.js App Router:** https://nextjs.org/docs/app
- **Modal Python Functions:** https://modal.com/docs/guide
- **Cloudinary Upload:** https://cloudinary.com/documentation/upload_videos

### Community

- **Modal Discord:** https://discord.gg/modal
- **Vercel Discord:** https://discord.gg/vercel
- **Next.js Discussions:** https://github.com/vercel/next.js/discussions

---

## 🎯 Next Steps

1. **Finish any planned changes** to the Python scripts
2. **Test the complete workflow** locally one more time
3. **Create Modal account** and test deploying a simple function
4. **Set up Next.js project** following Phase 1
5. **Implement API routes** following Phase 3-4
6. **Deploy to Vercel** following Phase 5
7. **Test in production** with a real video
8. **Share with users!**

---

**Estimated Total Time:** 8-10 hours spread over 2-3 days

**Difficulty:** Intermediate (familiarity with Next.js and Python helpful)

**Support:** Open issues on GitHub or reach out in Modal/Vercel communities

---

*Last updated: 2025-01-15*
*Version: 1.0*
