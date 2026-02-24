# Creative Cloner - Complete Workflow Guide

This guide provides step-by-step commands to execute the entire Creative Cloner workflow without AI assistance.

## 📋 Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed
2. **FFmpeg** installed (for video combination)
3. **API Keys** configured in `.agent/.env`:
   ```
   GEMINI_API_KEY=your_gemini_key_here
   KIE_API_KEY=your_kie_api_key_here
   AIRTABLE_API_TOKEN=your_airtable_token_here
   AIRTABLE_BASE_ID=your_airtable_base_id_here
   ```
4. **Dependencies** installed:
   ```bash
   pip install -r requirements.txt
   ```

## 🎬 Complete Workflow

### **Step 1: Analyze Inspiration Video**

Analyze the viral video you want to recreate using the SEALCaM framework.

```bash
python tools/analyze_video.py inputs/inspo.mp4
```

**What it does:**
- Analyzes video scenes (Subject, Environment, Action, Lighting, Camera, Music)
- Outputs analysis to `outputs/analysis.yaml`
- **Cost:** FREE (uses Gemini API for analysis)

**Expected Output:**
```
✅ Video analysis complete!
📄 Analysis saved to: outputs/analysis.yaml
```

**Review the output:**
```bash
# On Windows
type outputs\analysis.yaml

# On Mac/Linux
cat outputs/analysis.yaml
```

---

### **Step 2: Generate Prompts**

Create image and video generation prompts using your reference image.

```bash
python tools/create_prompts.py inputs/Ref.png
```

**What it does:**
- Analyzes your reference image (Ref.png)
- Creates image prompts for frame generation
- Creates video prompts for animation
- Outputs to `outputs/prompts.yaml`
- **Cost:** FREE (uses Gemini API)

**Expected Output:**
```
✅ Reference description: [Description of your reference image]
✅ Created 1 prompt pairs
💾 Prompts saved to: outputs/prompts.yaml
```

**Review the prompts:**
```bash
# On Windows
type outputs\prompts.yaml

# On Mac/Linux
cat outputs/prompts.yaml
```

---

### **Step 3: Log to Airtable**

Log prompts to Airtable for tracking and organization.

```bash
python tools/log_to_airtable.py --project-name "My Demo Project"
```

**What it does:**
- Uploads prompts to Airtable
- Creates records for each scene
- Clears existing records with same project name
- **Cost:** FREE

**Expected Output:**
```
✅ Successfully logged 1 records to Airtable
📋 AIRTABLE LOGGING SUMMARY
Total Scenes: 1
```

---

### **Step 4: Generate Images**

Generate static frames from your prompts.

#### **Option A: Test with Z-Image (Cheaper)**
```bash
# Dry run first (preview without spending)
python tools/generate_images.py --model z-image --dry-run

# Generate for real
python tools/generate_images.py --model z-image --project-name "My Demo Project"
```
**Cost:** ~$0.004 per image
**Note:** Does NOT support reference images

#### **Option B: Production with Nano Banana Pro (Recommended)**
```bash
# Dry run first
python tools/generate_images.py --model nano-banana-pro --reference inputs/Ref.png --dry-run

# Generate for real
python tools/generate_images.py --model nano-banana-pro --reference inputs/Ref.png --project-name "My Demo Project"
```
**Cost:** ~$0.09 per image
**Supports:** Reference image integration

**Expected Output:**
```
✅ Successful: 1, ❌ Failed: 0
💰 Actual cost: $0.09 (or $0.004 for z-image)
🖼️ Images uploaded to Airtable
📁 Images saved to: outputs/
```

---

### **Step 5: Generate Videos**

Animate your images into videos.

#### **Dry Run First (ALWAYS RECOMMENDED)**
```bash
python tools/generate_videos.py --dry-run --project-name "My Demo Project"
```

This shows you:
- Which images will be used
- Estimated costs
- What prompts will be sent

#### **Model Selection:**

**Option A: Sora 2 (OpenAI)**
```bash
python tools/generate_videos.py --model sora-2 --duration 10 --project-name "My Demo Project"
```
- **Cost:** ~$0.50 per 10-second video
- **Aspect Ratio:** Landscape
- **Duration:** 10 or 15 seconds
- **Features:** Good quality, watermark removal

**Option B: Kling 3.0 Standard (Recommended for Portrait)**
```bash
python tools/generate_videos.py --model kling-3.0-std --project-name "My Demo Project"
```
- **Cost:** ~$0.80 per video
- **Aspect Ratio:** 9:16 (Portrait)
- **Duration:** 10 seconds
- **Features:** Native sound generation, standard resolution

**Option C: Kling 3.0 Pro (Highest Quality)**
```bash
python tools/generate_videos.py --model kling-3.0-pro --project-name "My Demo Project"
```
- **Cost:** ~$1.50 per video
- **Aspect Ratio:** 9:16 (Portrait)
- **Duration:** 10 seconds
- **Features:** Native sound generation, higher resolution

**Expected Output:**
```
🎬 Creating video generation task...
⏳ Waiting for video generation to complete...
✅ Video generated successfully!
📹 Video uploaded to Airtable
💾 Video saved to: outputs/scene_1_....mp4
```

**Generation Time:** 3-5 minutes per video

---

### **Step 6: Combine Videos (Optional)**

If you have multiple scene videos, combine them into one final video.

#### **Preview First:**
```bash
python tools/combine_all.py --dry-run --project-name "My Demo Project"
```

#### **Combine Videos:**
```bash
# Basic combination
python tools/combine_all.py --project-name "My Demo Project"

# With background music
python tools/combine_all.py --project-name "My Demo Project" --music inputs/background.mp3

# With custom output location
python tools/combine_all.py --project-name "My Demo Project" --output final_videos/my_final_video.mp4
```

**What it does:**
- Combines all scene videos in order
- Optionally adds background music with fade-out
- Uses FFmpeg (local, no API costs)
- **Cost:** FREE

**Expected Output:**
```
✅ VIDEO COMBINATION COMPLETE!
📹 Final video: outputs/final_video.mp4
📊 Combined 3 video(s)
💾 File size: 25.50 MB
```

**Note:** If you only have 1 scene, this step is not needed.

---

## 💡 Quick Reference

### **Minimal Workflow (1 Scene, Production Quality)**

```bash
# 1. Analyze video
python tools/analyze_video.py inputs/inspo.mp4

# 2. Generate prompts
python tools/create_prompts.py inputs/Ref.png

# 3. Log to Airtable
python tools/log_to_airtable.py --project-name "Demo"

# 4. Generate images (with reference)
python tools/generate_images.py --model nano-banana-pro --reference inputs/Ref.png --project-name "Demo"

# 5. Generate videos (portrait, with sound)
python tools/generate_videos.py --model kling-3.0-std --project-name "Demo"
```

**Total Cost:** ~$0.89 per scene ($0.09 image + $0.80 video)

---

### **Budget Workflow (Testing)**

```bash
# Same steps 1-3 as above

# 4. Generate images (cheaper, no reference)
python tools/generate_images.py --model z-image --project-name "Demo"

# 5. Generate videos (cheaper)
python tools/generate_videos.py --model sora-2 --duration 10 --project-name "Demo"
```

**Total Cost:** ~$0.504 per scene ($0.004 image + $0.50 video)

---

## 🔍 Troubleshooting

### **Check API Keys**
```bash
# Windows
type .agent\.env

# Mac/Linux
cat .agent/.env
```

### **Verify FFmpeg Installation**
```bash
ffmpeg -version
```

### **Check Generated Files**
```bash
# Windows
dir outputs

# Mac/Linux
ls -lh outputs/
```

### **View Airtable Records**
Visit: `https://airtable.com/{your_base_id}`

---

## 📊 Cost Calculator

| Step | Model | Cost per Scene | Notes |
|------|-------|----------------|-------|
| 1. Analyze | Gemini 2.5 Flash | FREE | Video analysis |
| 2. Prompts | Gemini 2.5 Flash | FREE | Prompt generation |
| 3. Airtable | - | FREE | Logging |
| 4. Images | z-image | $0.004 | No reference support |
| 4. Images | nano-banana-pro | $0.09 | Supports reference |
| 5. Videos | sora-2 | $0.50 | Landscape, 10-15s |
| 5. Videos | kling-3.0-std | $0.80 | Portrait 9:16, sound |
| 5. Videos | kling-3.0-pro | $1.50 | Portrait 9:16, HQ |
| 6. Combine | FFmpeg | FREE | Local processing |

**Example Projects:**

- **1-scene test:** $0.504 (z-image + sora-2)
- **1-scene production:** $0.89 (nano-banana-pro + kling-3.0-std)
- **3-scene production:** $2.67 (3 × $0.89)

---

## 🎯 Tips for Showcasing

1. **Always run dry-run first** to show cost estimation
2. **Show Airtable updates** in real-time during demo
3. **Have backup videos** ready in case API is slow
4. **Prepare multiple reference images** to show flexibility
5. **Use --project-name** to keep demos organized
6. **Show the analysis.yaml** to explain AI understanding
7. **Compare models** (Sora 2 vs Kling 3.0) side-by-side

---

## 📁 Expected File Structure After Workflow

```
Creative Cloner/
├── inputs/
│   ├── inspo.mp4          # Your inspiration video
│   └── Ref.png            # Your reference image
├── outputs/
│   ├── analysis.yaml      # Video analysis
│   ├── prompts.yaml       # Generated prompts
│   ├── scene_1_....png    # Generated image
│   ├── scene_1_....mp4    # Generated video
│   └── final_video.mp4    # Combined video (if multiple scenes)
└── .agent/
    └── .env               # API keys (never commit!)
```

---

## ✅ Pre-Demo Checklist

- [ ] All API keys configured in `.agent/.env`
- [ ] FFmpeg installed and accessible
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Airtable base created with "Scenes" table
- [ ] Input files ready (`inspo.mp4`, `Ref.png`)
- [ ] Sufficient API credits for demo
- [ ] Test run completed successfully
- [ ] Backup videos prepared (in case of API issues)

---

## 🚀 Quick Demo Script

```bash
# Show analysis
python tools/analyze_video.py inputs/inspo.mp4
type outputs\analysis.yaml

# Generate prompts
python tools/create_prompts.py inputs/Ref.png
type outputs\prompts.yaml

# Log to Airtable (open Airtable in browser to show update)
python tools/log_to_airtable.py --project-name "Demo"

# Generate image (show dry-run first)
python tools/generate_images.py --model nano-banana-pro --reference inputs/Ref.png --dry-run
python tools/generate_images.py --model nano-banana-pro --reference inputs/Ref.png --project-name "Demo"

# Generate video (show dry-run first)
python tools/generate_videos.py --model kling-3.0-std --dry-run --project-name "Demo"
python tools/generate_videos.py --model kling-3.0-std --project-name "Demo"

# Show final output
dir outputs
```

---

## 🎓 Understanding the Output

### **analysis.yaml**
Contains detailed scene breakdown:
- Scene description
- Environment details
- Camera angles
- Lighting conditions
- Action/movement
- Duration

### **prompts.yaml**
Contains two prompts per scene:
- **image_prompt**: For generating static frames
- **video_prompt**: For animating frames

### **Airtable**
Tracks entire workflow:
- Scene information
- Generated prompts
- Image attachments
- Video attachments
- Project organization

---

**Last Updated:** 2026-02-25
**Version:** 1.0
**Tested With:** Kling 3.0 Standard, Nano Banana Pro
