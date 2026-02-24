---
name: Creative Cloner
description: Recreate viral videos with your own products or characters using AI
---

# Creative Cloner Skill

## Overview

This skill helps users recreate viral videos by replacing the original content with their own products, characters, or branding. The workflow analyzes a viral video, extracts scene descriptions, generates custom prompts, creates images using AI, animates them into videos, and combines everything into a final polished output.

**Complete Workflow:**
Analyze video → Generate prompts → Create images → Animate videos → Combine → Done!

**Typical Project:**
- Input: 1 viral video (any format)
- Output: 1 recreated video with your custom content
- Cost: ~$1.00 - $1.18 for 2 scenes
- Time: ~10 minutes

---

## Folder Structure

```
Creative Cloner/
├── .agent/
│   ├── .env                    # API keys (user creates from .env.example)
│   └── skills/
│       └── creative-cloner/
│           └── SKILL.md        # This file
├── docs/                       # Internal dev documentation (gitignored)
├── inputs/                     # User's input videos (gitignored)
├── outputs/                    # Generated final videos (gitignored)
├── prompts/                    # Generated JSON prompt files
├── tools/                      # Python workflow scripts
│   ├── analyze_video.py        # Step 1: Extract scenes from video
│   ├── generate_prompts.py     # Step 2a: Create image/video prompts
│   ├── log_to_airtable.py      # Step 2b: Upload to tracking database
│   ├── generate_images.py      # Step 3a: Generate images from prompts
│   ├── generate_videos.py      # Step 3b: Animate images into videos
│   ├── combine_all.py          # Step 4: Stitch all videos together
│   └── verify_setup.py         # Prerequisites checker
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions
├── LICENSE                     # MIT License
├── README.md                   # User-facing documentation
└── requirements.txt            # Python dependencies
```

---

## Critical Rules

### 🚨 ALWAYS DO

1. **Cost Approval Required**
   - ALWAYS get explicit user approval before any API call that costs money
   - ALWAYS show estimated cost before proceeding
   - ALWAYS run `--dry-run` mode first to preview without spending

2. **Test Before Production**
   - ALWAYS start with `--test-mode` using cheap models (z-image: $0.004/image)
   - ALWAYS generate 1 scene first before doing all scenes
   - ALWAYS verify images look good before generating videos

3. **Prerequisites Check**
   - ALWAYS verify `.agent/.env` exists before running any tool
   - ALWAYS check FFmpeg installed before running `combine_all.py`
   - ALWAYS verify Python dependencies installed

4. **User Checkpoints**
   - Get approval after Step 1 (analyze video) before generating prompts
   - Get approval after Step 2 (prompts) before generating images
   - Get approval after Step 3a (images) before generating videos
   - Get approval after Step 3b (videos) before combining

### 🚫 NEVER DO

1. **Never** skip cost approval steps
2. **Never** generate videos before verifying images are correct
3. **Never** use production models without testing first
4. **Never** proceed if `.env` file is missing or has placeholder values
5. **Never** assume FFmpeg is installed - always verify first
6. **Never** batch process all scenes without testing one first

### 💰 Cost Warnings

Before running these commands, WARN USER about costs:

- `generate_images.py --model nano-banana-pro`: **$0.09 per image**
- `generate_videos.py --model sora-2`: **~$0.50 per 10s video**
- `generate_images.py --model z-image --test-mode`: **$0.004 per image** ✅ Cheap testing

**Example warning:**
```
⚠️  COST ALERT: About to generate 2 images using nano-banana-pro
Estimated cost: 2 images × $0.09 = $0.18
Proceed? (y/n)
```

---

## Step-by-Step Process

### Prerequisites (One-Time Setup)

1. **Install FFmpeg**
   - Windows: Download from https://ffmpeg.org/download.html, add to PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .agent/.env
   # Edit .agent/.env and add API keys
   ```

4. **Get API Keys**
   - Gemini: https://ai.google.dev/
   - Kie.ai: https://kie.ai/api-key
   - Airtable: https://airtable.com/account

5. **Set Up Airtable Base**
   - Create a new base
   - Add table with required fields (see Database Schema below)
   - Get base ID from URL: `https://airtable.com/{BASE_ID}/...`

6. **Verify Setup**
   ```bash
   python tools/verify_setup.py
   ```
   Must show all checks passed ✅

### Workflow Steps

#### **Step 1: Analyze Video** 📹
```bash
python tools/analyze_video.py
```

**What it does:**
- Prompts user to select video from `inputs/` folder
- Uploads to Gemini API for scene analysis
- Extracts key scenes with descriptions
- Saves to `prompts/analyzed_prompts.json`

**Output:** JSON file with scenes like:
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "scene_description": "Close-up of hands holding a product..."
    }
  ]
}
```

**Checkpoint:** Ask user to review `analyzed_prompts.json` before proceeding.

---

#### **Step 2a: Generate Prompts** 🎨
```bash
python tools/generate_prompts.py --input prompts/analyzed_prompts.json
```

**What it does:**
- Takes scene descriptions
- Uses Gemini to create detailed image generation prompts
- Uses Gemini to create video animation prompts
- Saves to `prompts/final_prompts.json`

**Output:** JSON with detailed prompts:
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "scene_description": "...",
      "image_prompt": "Ultra-detailed photorealistic image of...",
      "video_prompt": "Camera slowly zooms in while..."
    }
  ]
}
```

**Checkpoint:** Ask user to review prompts before logging to Airtable.

---

#### **Step 2b: Log to Airtable** 📊
```bash
python tools/log_to_airtable.py --project-name "My Viral Video Clone"
```

**What it does:**
- Uploads all scenes to Airtable for tracking
- Creates one record per scene
- Sets project name for filtering
- Prepares for image/video attachment uploads

**Output:** Airtable records created with status confirmation

**Checkpoint:** Ask user to verify Airtable records created successfully.

---

#### **Step 3a: Generate Images** 🖼️

**ALWAYS TEST FIRST:**
```bash
# Test with cheap model ($0.004/image)
python tools/generate_images.py --model z-image --test-mode
```

**Production quality:**
```bash
# Get user approval first! ($0.09/image)
python tools/generate_images.py --model nano-banana-pro --resolution 2K
```

**What it does:**
- Reads prompts from Airtable
- Generates images via Kie.ai API
- Polls for completion (smart retry logic)
- Downloads and saves images locally
- Uploads images back to Airtable (start_image field)

**Models:**
- `z-image`: $0.004/image (testing)
- `nano-banana-pro`: $0.09/image (production quality)

**Checkpoint:**
1. After test mode: Show user test images, ask if quality is acceptable
2. Before production: Get explicit cost approval
3. After production: Ask user to review all images before video generation

---

#### **Step 3b: Generate Videos** 🎬

**ALWAYS DRY-RUN FIRST:**
```bash
# Preview what will be generated (no cost)
python tools/generate_videos.py --dry-run
```

**Generate videos:**
```bash
# Get user approval first! (~$0.50/video)
python tools/generate_videos.py --model sora-2 --duration 10
```

**What it does:**
- Reads image attachments from Airtable
- Generates video animations via Kie.ai API
- Uses video prompts for animation instructions
- Polls for completion (can take several minutes)
- Downloads and saves videos locally
- Uploads videos back to Airtable (scene_video field)

**Options:**
- `--duration 10`: 10-second videos (~$0.50 each)
- `--duration 15`: 15-second videos (~$0.75 each)
- `--model sora-2`: Current best model

**Checkpoint:**
1. After dry-run: Show user what will be generated and cost estimate
2. Before generation: Get explicit cost approval
3. After generation: Ask user to review all scene videos

---

#### **Step 4: Combine Videos** 🎞️

**ALWAYS PREVIEW FIRST:**
```bash
# Preview combination order (no cost, uses FFmpeg locally)
python tools/combine_all.py --dry-run
```

**Combine all scenes:**
```bash
python tools/combine_all.py

# With background music
python tools/combine_all.py --music inputs/background.mp3
```

**What it does:**
- Downloads all scene videos from Airtable
- Uses FFmpeg to concatenate videos in order
- Optionally adds background music
- Outputs final video to `outputs/`
- **100% FREE** (runs locally)

**Output:** `outputs/final_combined_video.mp4`

**Checkpoint:** Ask user to review final video and confirm satisfied with result.

---

## Available Tools

### `verify_setup.py`
**Purpose:** Validate all prerequisites are installed and configured

**Usage:**
```bash
python tools/verify_setup.py
```

**Checks:**
- ✅ Python 3.8+
- ✅ FFmpeg installed
- ✅ Python dependencies (google-genai, pyairtable, requests, etc.)
- ✅ `.env` file exists with all required keys
- ✅ Required directories exist

**Exit codes:**
- 0: All checks passed
- 1: Some checks failed

---

### `analyze_video.py`
**Purpose:** Extract scene descriptions from viral video using Gemini

**Usage:**
```bash
python tools/analyze_video.py
```

**Interactive prompts:**
1. Lists all videos in `inputs/` folder
2. User selects which video to analyze
3. Uploads to Gemini Flash 2.0
4. Extracts 2-3 key scenes

**Output:** `prompts/analyzed_prompts.json`

**Dependencies:**
- `GEMINI_API_KEY` in `.env`
- Video file in `inputs/` folder

**Error handling:**
- Validates video file exists
- Checks Gemini API connectivity
- Retries on transient errors

---

### `generate_prompts.py`
**Purpose:** Convert scene descriptions into detailed image/video prompts

**Usage:**
```bash
python tools/generate_prompts.py --input prompts/analyzed_prompts.json
```

**Arguments:**
- `--input`: Path to analyzed prompts JSON (required)

**What it generates:**
- **Image prompts:** Ultra-detailed, photorealistic descriptions
- **Video prompts:** Camera movements, animations, transitions

**Output:** `prompts/final_prompts.json`

**Dependencies:**
- `GEMINI_API_KEY` in `.env`

---

### `log_to_airtable.py`
**Purpose:** Upload scene prompts to Airtable for tracking

**Usage:**
```bash
python tools/log_to_airtable.py --project-name "Project Name"
```

**Arguments:**
- `--project-name`: Name for this project (required)

**What it does:**
- Reads `prompts/final_prompts.json`
- Creates one Airtable record per scene
- Sets project name for filtering

**Dependencies:**
- `AIRTABLE_API_TOKEN` in `.env`
- `AIRTABLE_BASE_ID` in `.env`
- Airtable base with correct schema

**Error handling:**
- Validates Airtable connection
- Checks base and table exist
- Retries on rate limits

---

### `generate_images.py`
**Purpose:** Generate images from prompts using Kie.ai API

**Usage:**
```bash
# Test mode (cheap)
python tools/generate_images.py --model z-image --test-mode

# Production
python tools/generate_images.py --model nano-banana-pro --resolution 2K
```

**Arguments:**
- `--model`: Image model (z-image or nano-banana-pro)
- `--resolution`: 1K, 2K, or 4K (default: 2K)
- `--test-mode`: Generate only first scene (for testing)

**Models & Costs:**
- `z-image`: $0.004/image (fast, lower quality)
- `nano-banana-pro`: $0.09/image (high quality, recommended)

**What it does:**
1. Reads scenes from Airtable
2. For each scene:
   - Submits image generation request to Kie.ai
   - Polls for completion (with smart backoff)
   - Downloads generated image
   - Uploads image to Airtable (start_image field)

**Dependencies:**
- `KIE_API_KEY` in `.env`
- `AIRTABLE_API_TOKEN` in `.env`
- Airtable records from `log_to_airtable.py`

**Error handling:**
- Validates API key
- Handles generation failures gracefully
- Retries on network errors
- Skips already-generated images

---

### `generate_videos.py`
**Purpose:** Animate images into videos using Kie.ai API

**Usage:**
```bash
# Dry run (no cost)
python tools/generate_videos.py --dry-run

# Generate
python tools/generate_videos.py --model sora-2 --duration 10
```

**Arguments:**
- `--model`: Video model (sora-2)
- `--duration`: 10 or 15 seconds (default: 10)
- `--dry-run`: Preview without generating

**Costs:**
- 10s video: ~$0.50 each
- 15s video: ~$0.75 each

**What it does:**
1. Reads scenes with images from Airtable
2. For each scene:
   - Downloads start_image
   - Submits video generation request to Kie.ai
   - Polls for completion (can take 5-10 minutes)
   - Downloads generated video
   - Uploads video to Airtable (scene_video field)

**Dependencies:**
- `KIE_API_KEY` in `.env`
- `AIRTABLE_API_TOKEN` in `.env`
- Images must exist in Airtable from `generate_images.py`

**Error handling:**
- Validates images exist before generating
- Handles long-running generation jobs
- Smart polling with exponential backoff
- Retries on transient failures
- Skips already-generated videos

---

### `combine_all.py`
**Purpose:** Stitch all scene videos into final output using FFmpeg

**Usage:**
```bash
# Dry run
python tools/combine_all.py --dry-run

# Combine
python tools/combine_all.py

# With background music
python tools/combine_all.py --music inputs/background.mp3
```

**Arguments:**
- `--dry-run`: Preview without combining
- `--music`: Path to background music file (optional)

**What it does:**
1. Downloads all scene videos from Airtable
2. Saves to `outputs/scene_1.mp4`, `outputs/scene_2.mp4`, etc.
3. Uses FFmpeg to concatenate in order
4. Optionally adds background music
5. Outputs final video to `outputs/final_combined_video.mp4`

**Dependencies:**
- FFmpeg installed and in PATH
- `AIRTABLE_API_TOKEN` in `.env`
- Videos must exist in Airtable from `generate_videos.py`

**Cost:** FREE (runs locally)

**Error handling:**
- Validates FFmpeg installed
- Checks all scene videos exist
- Verifies output directory writable
- Handles FFmpeg errors gracefully

---

## API/Integration Details

### Gemini API (Video Analysis)

**Endpoint:** Google AI Studio API
**Model:** `gemini-2.0-flash-exp`

**Authentication:**
```python
import google.genai as genai
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
```

**Video Analysis Request:**
```python
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Upload video file
video_file = genai.upload_file(path=video_path)

# Generate scene analysis
response = model.generate_content([
    video_file,
    "Analyze this viral video and extract 2-3 key scenes..."
])
```

**Prompt Engineering:**
- Request structured JSON output
- Ask for scene numbers and descriptions
- Focus on key visual moments
- Ignore audio/music

**Rate Limits:**
- Free tier: 15 requests/minute
- Paid tier: Higher limits

**Pricing:**
- Flash model: Very low cost (~$0.01 per video analysis)

---

### Kie.ai API (Image & Video Generation)

**Base URL:** `https://api.kie.ai`
**Dashboard:** https://kie.ai/dashboard

**Authentication:**
```python
headers = {
    'Authorization': f'Bearer {KIE_API_KEY}',
    'Content-Type': 'application/json'
}
```

#### Image Generation

**Endpoint:** `POST https://api.kie.ai/v1/images/generate`

**Request Payload:**
```json
{
  "model": "nano-banana-pro",
  "prompt": "Ultra-detailed photorealistic image of...",
  "resolution": "2K",
  "num_outputs": 1
}
```

**Response:**
```json
{
  "id": "img_abc123",
  "status": "processing",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Status Check:** `GET https://api.kie.ai/v1/images/{id}`

**Response when complete:**
```json
{
  "id": "img_abc123",
  "status": "completed",
  "output": {
    "images": [
      {
        "url": "https://cdn.kie.ai/outputs/img_abc123.png"
      }
    ]
  }
}
```

**Models:**
- `z-image`: Fast, cheap ($0.004), lower quality
- `nano-banana-pro`: High quality ($0.09), recommended

**Resolutions:**
- `1K`: 1024x1024
- `2K`: 2048x2048 (recommended)
- `4K`: 4096x4096 (expensive)

**Polling Strategy:**
```python
# Check status every 5s for first 30s
# Then every 10s for next 60s
# Then every 30s until complete or timeout
```

#### Video Generation

**Endpoint:** `POST https://api.kie.ai/v1/videos/generate`

**Request Payload:**
```json
{
  "model": "sora-2",
  "start_image_url": "https://...",
  "prompt": "Camera slowly zooms in while...",
  "duration": 10,
  "resolution": "1080p"
}
```

**Response:**
```json
{
  "id": "vid_xyz789",
  "status": "queued",
  "created_at": "2025-01-15T10:35:00Z"
}
```

**Status Check:** `GET https://api.kie.ai/v1/videos/{id}`

**Response when complete:**
```json
{
  "id": "vid_xyz789",
  "status": "completed",
  "output": {
    "video_url": "https://cdn.kie.ai/outputs/vid_xyz789.mp4"
  }
}
```

**Models:**
- `sora-2`: Current best model (~$0.50 for 10s)

**Durations:**
- 10 seconds: ~$0.50
- 15 seconds: ~$0.75

**Polling Strategy:**
```python
# Video generation takes longer
# Check every 30s for first 5 minutes
# Then every 60s until complete or timeout (20 min max)
```

**Rate Limits:**
- Concurrent generations: 3 images, 1 video
- Queue: Up to 10 pending requests

**Error Codes:**
- `400`: Invalid request (check prompt/image)
- `402`: Insufficient credits
- `429`: Rate limit exceeded
- `500`: Server error (retry)

---

### Airtable API (Project Tracking)

**Base URL:** `https://api.airtable.com/v0`
**Endpoint:** `/{BASE_ID}/{TABLE_NAME}`

**Authentication:**
```python
from pyairtable import Api

api = Api(os.getenv('AIRTABLE_API_TOKEN'))
table = api.table(
    base_id=os.getenv('AIRTABLE_BASE_ID'),
    table_name='Scenes'
)
```

**Create Record:**
```python
record = table.create({
    'scene_number': 1,
    'scene_description': 'Close-up of hands holding product',
    'image_prompt': 'Ultra-detailed photorealistic...',
    'video_prompt': 'Camera slowly zooms in...',
    'project_name': 'My Viral Video Clone'
})
```

**Update Record (Add Attachment):**
```python
table.update(record['id'], {
    'start_image': [{
        'url': 'https://cdn.kie.ai/outputs/img_abc123.png'
    }]
})
```

**Query Records:**
```python
# Get all scenes for a project, sorted by scene number
records = table.all(
    formula="AND({project_name}='My Viral Video Clone')",
    sort=['scene_number']
)
```

**Rate Limits:**
- 5 requests/second per base
- Automatically handled by pyairtable

---

## Database/Storage Schema

### Airtable Base Structure

**Table Name:** `Scenes` (or any name, configurable)

**Required Fields:**

| Field Name | Type | Description | Example |
|------------|------|-------------|---------|
| `scene_number` | Number | Scene sequence order | `1`, `2`, `3` |
| `scene_description` | Long text | Original scene analysis | "Close-up of hands holding product against white background" |
| `image_prompt` | Long text | Detailed image generation prompt | "Ultra-detailed photorealistic image of hands holding iPhone 15 Pro..." |
| `video_prompt` | Long text | Video animation instructions | "Camera slowly zooms in while maintaining focus on product" |
| `start_image` | Attachment | Generated image from Kie.ai | `[{url: "https://..."}]` |
| `scene_video` | Attachment | Generated video from Kie.ai | `[{url: "https://..."}]` |
| `project_name` | Single line text | Project identifier for filtering | "My Viral Video Clone" |

**Optional Fields (for tracking):**

| Field Name | Type | Description |
|------------|------|-------------|
| `image_generation_status` | Single select | "pending", "processing", "completed", "failed" |
| `video_generation_status` | Single select | "pending", "processing", "completed", "failed" |
| `created_at` | Created time | Auto-populated timestamp |
| `last_modified` | Last modified time | Auto-updated timestamp |
| `notes` | Long text | Manual notes/adjustments |

**Setup Instructions:**
1. Create new Airtable base
2. Add all required fields with exact names and types
3. Get base ID from URL: `https://airtable.com/{BASE_ID}/...`
4. Add base ID to `.agent/.env`

**View Configuration:**
- Grid view: All fields visible
- Gallery view: Show `start_image` and `scene_video` thumbnails
- Filter by `project_name` to see specific projects

---

### Local File Structure

**Inputs:**
```
inputs/
├── viral_video_1.mp4       # User-provided viral videos
├── viral_video_2.mov
└── background.mp3          # Optional background music
```

**Prompts (Generated):**
```
prompts/
├── analyzed_prompts.json   # Step 1 output (scene descriptions)
└── final_prompts.json      # Step 2a output (image/video prompts)
```

**Outputs (Generated):**
```
outputs/
├── scene_1.mp4             # Downloaded scene videos
├── scene_2.mp4
├── scene_3.mp4
└── final_combined_video.mp4  # Final stitched output
```

**JSON Schema (`final_prompts.json`):**
```json
{
  "scenes": [
    {
      "scene_number": 1,
      "scene_description": "Original analysis from Gemini",
      "image_prompt": "Detailed image generation prompt",
      "video_prompt": "Camera movement and animation instructions"
    }
  ]
}
```

---

## Quick Start

### New User Getting Started

1. **Clone repository and install:**
   ```bash
   git clone https://github.com/dkumarvaishnav/creative-cloner.git
   cd creative-cloner
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .agent/.env
   # Edit .agent/.env with your API keys
   ```

3. **Verify setup:**
   ```bash
   python tools/verify_setup.py
   # Must show all ✅ checks passed
   ```

4. **Place input video:**
   ```bash
   # Copy your viral video to inputs/
   cp ~/Downloads/viral_tiktok.mp4 inputs/
   ```

5. **Run complete workflow:**
   ```bash
   # Step 1: Analyze
   python tools/analyze_video.py

   # Step 2: Generate prompts and log
   python tools/generate_prompts.py --input prompts/analyzed_prompts.json
   python tools/log_to_airtable.py --project-name "My First Clone"

   # Step 3: Generate content (TEST MODE FIRST!)
   python tools/generate_images.py --model z-image --test-mode
   # Review test images, then:
   python tools/generate_images.py --model nano-banana-pro --resolution 2K

   # Generate videos
   python tools/generate_videos.py --dry-run  # Preview first
   python tools/generate_videos.py --model sora-2 --duration 10

   # Step 4: Combine
   python tools/combine_all.py --dry-run  # Preview
   python tools/combine_all.py
   ```

6. **Find output:**
   ```bash
   # Final video is in outputs/final_combined_video.mp4
   ```

---

### Claude Agent Instructions

When a user invokes this skill:

1. **First time setup:**
   - Run `verify_setup.py` to check prerequisites
   - If any checks fail, guide user through setup
   - Confirm all API keys are configured

2. **Running the workflow:**
   - Always ask which step user wants to run
   - Show costs BEFORE running any paid operations
   - Always use test mode first for images
   - Always use dry-run first for videos
   - Get explicit approval at each checkpoint

3. **Error handling:**
   - If API key missing/invalid: Guide to setup
   - If FFmpeg missing: Provide installation instructions
   - If Airtable schema wrong: Show required fields
   - If generation fails: Check API status and retry

4. **Best practices:**
   - Start with 1 scene before processing all scenes
   - Use `z-image` for testing ($0.004)
   - Use 10s videos instead of 15s (cheaper)
   - Always preview with --dry-run before spending

5. **Output locations:**
   - Prompts: `prompts/*.json`
   - Images/Videos: Airtable + `outputs/`
   - Final video: `outputs/final_combined_video.mp4`

---

## Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found"**
- Solution: Ensure `.agent/.env` exists with valid API key
- Get key from: https://ai.google.dev/

**"FFmpeg not found"**
- Solution: Install FFmpeg and add to PATH
- Verify: `ffmpeg -version`

**"Airtable base not found"**
- Solution: Check `AIRTABLE_BASE_ID` is correct
- Format: `app...` (starts with "app")

**"Image generation failed"**
- Check Kie.ai dashboard for credit balance
- Verify image prompt isn't too long (max ~500 chars)
- Try with `z-image` model first

**"Video generation timeout"**
- Videos can take 5-10 minutes
- Check Kie.ai dashboard for status
- Re-run script - it will skip completed videos

**"Combine fails with codec error"**
- Ensure all scene videos downloaded
- Check FFmpeg installed correctly
- Verify videos are valid MP4 files

---

## Cost Optimization Tips

1. **Always test with cheap models first:**
   - `z-image` costs 22x less than `nano-banana-pro`
   - Verify prompts work before using expensive models

2. **Start with 1 scene:**
   - Use `--test-mode` to generate only first scene
   - Confirm quality before processing all scenes

3. **Use 10s videos:**
   - 10s costs ~$0.50 vs 15s costs ~$0.75
   - Most viral videos use quick cuts anyway

4. **Batch operations:**
   - Generate all images in one run
   - Generate all videos in one run
   - Reduces API overhead

5. **Check Airtable before re-running:**
   - Scripts skip already-generated content
   - Avoids double-charging

---

## Next Steps / Extensions

**Possible enhancements:**
- Audio extraction and transcription
- Automatic caption generation
- Multi-language support
- Batch processing multiple videos
- Custom brand templates
- Automatic social media posting

**Current limitations:**
- Maximum ~10 scenes per video (cost constraints)
- No audio analysis (only visual)
- Requires manual Airtable setup
- No built-in video editing (transitions, effects)

---

## Resources

- **Kie.ai Documentation:** https://docs.kie.ai/
- **Kie.ai Pricing:** https://kie.ai/pricing
- **Kie.ai Dashboard:** https://kie.ai/dashboard
- **Google Gemini API:** https://ai.google.dev/
- **Airtable API Docs:** https://airtable.com/api
- **FFmpeg Documentation:** https://ffmpeg.org/documentation.html
- **GitHub Repository:** https://github.com/dkumarvaishnav/creative-cloner

---

*Last updated: 2025-01-15*
