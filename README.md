# 🎨 Creative Cloner

Recreate viral videos with your own products or characters using AI.

**Workflow:** Analyze video → Generate prompts → Create images → Animate videos → Combine → Done!

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for Gemini, Kie.ai, and Airtable
- FFmpeg (for video combining)

### Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment (.agent/.env)
GEMINI_API_KEY=your_key
KIE_API_KEY=your_key
AIRTABLE_API_TOKEN=your_token
AIRTABLE_BASE_ID=your_base_id

# 3. Set up Airtable table with fields:
# - scene_number (Number)
# - scene_description (Long text)
# - image_prompt (Long text)
# - video_prompt (Long text)
# - start_image (Attachment)
# - scene_video (Attachment)
# - project_name (Single line text)
```

---

## 📖 Workflow Steps

### Step 1: Analyze Video
```bash
# Place video in inputs/ folder
python tools/analyze_video.py
```
Analyzes viral video and extracts scene descriptions.

### Step 2a: Generate Prompts
```bash
python tools/generate_prompts.py --input prompts/analyzed_prompts.json
```
Creates detailed image and video prompts.

### Step 2b: Log to Airtable
```bash
python tools/log_to_airtable.py --project-name "My Project"
```
Uploads prompts to Airtable for tracking.

### Step 3a: Generate Images
```bash
# Test with cheap model first
python tools/generate_images.py --model z-image --test-mode
# Cost: $0.004/image

# Production quality
python tools/generate_images.py --model nano-banana-pro --resolution 2K
# Cost: $0.09/image
```
Creates images from prompts using AI generation.

### Step 3b: Generate Videos
```bash
# Always dry-run first
python tools/generate_videos.py --dry-run

# Generate videos
python tools/generate_videos.py --model sora-2 --duration 10
# Cost: ~$0.50/video (10s)
```
Animates images into videos.

### Step 4: Combine Videos
```bash
# Preview first
python tools/combine_all.py --dry-run

# Combine all scene videos
python tools/combine_all.py

# With background music
python tools/combine_all.py --music inputs/background.mp3
# Cost: FREE (local FFmpeg)
```
Stitches all videos into final output.

---

## 💰 Typical Costs

**2-scene project:**
- Test: $0.008 (z-image) + $1.00 (videos) = **$1.01**
- Production: $0.18 (nano-banana-pro) + $1.00 (videos) = **$1.18**

**Models:**
- `z-image`: $0.004/image (testing)
- `nano-banana-pro`: $0.09/image (production)
- `sora-2`: ~$0.50/video (10s or 15s)
- `combine_all.py`: FREE (local FFmpeg)

---

## 🛡️ Safety Features

- **Cost approval required** before spending credits
- **Dry-run mode** to preview without spending
- **Test mode** with cheap models
- **Smart polling** for API efficiency
- **Error recovery** with detailed messages

---

## 💡 Pro Tips

1. Always use `--dry-run` first
2. Test with `z-image` ($0.004) before production
3. Start with 1 scene before generating all
4. Use 10s duration (cheaper than 15s)
5. Check Airtable after each step

---

## 📁 Structure

```
Creative Cloner/
├── tools/              # Python scripts
├── inputs/             # Your input videos
├── outputs/            # Generated videos
├── .agent/.env         # API keys (create this)
└── README.md           # This file
```

---

## 🔗 Resources

- Kie.ai Dashboard: https://kie.ai/dashboard
- Kie.ai Pricing: https://kie.ai/pricing
- Airtable API: https://airtable.com/api
- Google Gemini: https://ai.google.dev/

---

## 📝 Example Usage

```bash
# Complete workflow
python tools/analyze_video.py
python tools/log_to_airtable.py
python tools/generate_images.py --model z-image --test-mode
python tools/generate_videos.py --model sora-2
python tools/combine_all.py --music inputs/background.mp3

# Total cost: ~$1.00 for 2 scenes
# Total time: ~10 minutes
```
