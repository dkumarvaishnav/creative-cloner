# 🎨 Creative Cloner

Recreate viral videos with your own products or characters using AI.

**Workflow:** Analyze video → Generate prompts → Create images → Animate videos → Combine → Done!

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for video combining - see installation below)
- API keys for Gemini, Kie.ai, and Airtable

### Installation

#### 1. Install FFmpeg

**Windows:**
```bash
# Download from: https://ffmpeg.org/download.html
# Extract and add to PATH, then verify:
ffmpeg -version
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

#### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Set Up Environment Variables

```bash
# Copy the example file
cp .env.example .agent/.env

# Edit .agent/.env and add your API keys:
GEMINI_API_KEY=your_gemini_key
KIE_API_KEY=your_kie_key
AIRTABLE_API_TOKEN=your_airtable_token
AIRTABLE_BASE_ID=your_base_id
```

**Get your API keys:**
- Gemini: https://ai.google.dev/
- Kie.ai: https://kie.ai/api-key
- Airtable: https://airtable.com/account

# 4. Set up Airtable table with fields:
# - scene_number (Number)
# - scene_description (Long text)
# - image_prompt (Long text)
# - video_prompt (Long text)
# - start_image (Attachment)
# - scene_video (Attachment)
# - project_name (Single line text)

# 5. Verify setup
python tools/verify_setup.py
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

# Generate videos with Sora 2
python tools/generate_videos.py --model sora-2 --duration 10
# Cost: ~$0.50/video (10s)

# Generate with Kling 3.0 Standard (recommended)
python tools/generate_videos.py --model kling-3.0-std
# Cost: ~$0.80/video

# Generate with Kling 3.0 Pro (higher quality)
python tools/generate_videos.py --model kling-3.0-pro
# Cost: ~$1.50/video
```
Animates images into videos using AI models.

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

**Image Models:**
- `z-image`: $0.004/image (testing, no reference image support)
- `nano-banana-pro`: $0.09/image (production, supports reference images)

**Video Models:**
- `sora-2`: ~$0.50/video (10s or 15s, OpenAI Sora 2)
- `kling-3.0-std`: ~$0.80/video (Kling 3.0 Standard)
- `kling-3.0-pro`: ~$1.50/video (Kling 3.0 Pro, higher quality)

**Other:**
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

---

## 🤖 Using as a Claude Code Skill

Creative Cloner is packaged as a **Claude Code Cloud Skill** for easy sharing and reuse.

### What's a Cloud Skill?

A self-contained workflow that Claude Code can execute autonomously with:
- Complete documentation in [`.agent/skills/creative-cloner/SKILL.md`](.agent/skills/creative-cloner/SKILL.md)
- All API integrations (Gemini, Kie.ai, Airtable)
- Safety rules and cost approvals
- Step-by-step guidance

### Quick Install (For Others)

Anyone can use your skill:

```bash
# Clone the repository
git clone https://github.com/dkumarvaishnav/creative-cloner.git
cd creative-cloner

# Install and verify
pip install -r requirements.txt
cp .env.example .agent/.env
# Edit .agent/.env with your API keys
python tools/verify_setup.py
```

### Using with Claude Code

1. **Open Claude Code in project directory:**
   ```bash
   claude-code
   ```

2. **Ask Claude for help:**
   ```
   "Help me clone a viral video using Creative Cloner"
   ```

3. **Claude will:**
   - Read the SKILL.md documentation
   - Guide you through each step
   - Warn about costs before spending
   - Execute commands with your approval
   - Handle errors and retries

### Sharing Your Skill

**Share via GitHub:**
- Repository: https://github.com/dkumarvaishnav/creative-cloner
- Skill Docs: [`.agent/skills/creative-cloner/SKILL.md`](.agent/skills/creative-cloner/SKILL.md)

**For complete details on sharing, installing, and using as a cloud skill:**
📖 **[Read the Cloud Skill Guide](CLOUD_SKILL_GUIDE.md)**

Topics covered:
- Installing from GitHub
- Using in Claude Code
- Forking and customizing
- Publishing to cloud registry (future)
- Distribution strategies
- Monetization options

---

## 📚 Documentation

- **[README.md](README.md)** - Quick start and workflow steps (this file)
- **[SKILL.md](.agent/skills/creative-cloner/SKILL.md)** - Complete skill documentation for Claude Code
- **[CLOUD_SKILL_GUIDE.md](CLOUD_SKILL_GUIDE.md)** - Sharing and using as a cloud skill
- **[LICENSE](LICENSE)** - MIT License
