# 🌐 Creative Cloner - Cloud Skill Guide

Complete guide for sharing and using Creative Cloner as a Claude Code Cloud Skill.

---

## Table of Contents

1. [What is a Cloud Skill?](#what-is-a-cloud-skill)
2. [Using the Skill Locally](#using-the-skill-locally)
3. [Sharing via GitHub](#sharing-via-github)
4. [Installing Someone Else's Skill](#installing-someone-elses-skill)
5. [Using in Claude Code](#using-in-claude-code)
6. [Publishing to Cloud (Future)](#publishing-to-cloud-future)

---

## What is a Cloud Skill?

A **Cloud Skill** is a packaged, reusable workflow that Claude Code can execute autonomously. The Creative Cloner skill includes:

- **SKILL.md**: Complete workflow documentation with API details, tools, and step-by-step instructions
- **Tools**: 7 Python scripts that execute each workflow step
- **Schema**: Airtable database structure for tracking
- **Safety Rules**: Cost approvals, checkpoints, error handling

**Benefits:**
- ✅ Reusable across projects
- ✅ Shareable with other users
- ✅ Self-contained documentation
- ✅ Claude Code can guide users through the entire workflow

---

## Using the Skill Locally

### Current Setup

Your skill is already configured at:
```
c:\Users\dkuma\Desktop\Creative Cloner\.agent\skills\creative-cloner\SKILL.md
```

### How to Use

**Option 1: Direct Command Execution**
```bash
# Just run the workflow commands directly
python tools/verify_setup.py
python tools/analyze_video.py
python tools/generate_images.py --model z-image --test-mode
# etc...
```

**Option 2: Claude Code Guidance**

1. Open Claude Code in the project directory:
   ```bash
   cd "c:\Users\dkuma\Desktop\Creative Cloner"
   claude-code
   ```

2. Ask Claude to help:
   ```
   "Help me clone a viral video using the Creative Cloner workflow"
   ```

3. Claude will:
   - Read `.agent\skills\creative-cloner\SKILL.md`
   - Understand the complete workflow
   - Guide you through each step with cost warnings
   - Execute commands safely with your approval

---

## Sharing via GitHub

### Your Skill is Already Shared! ✅

**Repository:** https://github.com/dkumarvaishnav/creative-cloner

**What's included:**
- Complete workflow code (`tools/*.py`)
- Skill documentation (`.agent/skills/creative-cloner/SKILL.md`)
- Setup instructions (`README.md`)
- Environment template (`.env.example`)
- Verification script (`tools/verify_setup.py`)

### How Others Can Find It

**Share this link:**
```
🎬 Creative Cloner - Recreate viral videos with AI

GitHub: https://github.com/dkumarvaishnav/creative-cloner
Skill Docs: https://github.com/dkumarvaishnav/creative-cloner/blob/master/.agent/skills/creative-cloner/SKILL.md

Workflow: Analyze video → Generate prompts → Create images → Animate videos → Combine → Done!
Cost: ~$1 per 2-scene video
Time: ~10 minutes
```

### Keep It Updated

When you make improvements:
```bash
cd "c:\Users\dkuma\Desktop\Creative Cloner"
git add .
git commit -m "Update skill: <description of changes>"
git push
```

---

## Installing Someone Else's Skill

### Method 1: Clone the Entire Repository (Recommended)

This gives you the complete workflow with all tools:

```bash
# Clone to your desired location
cd ~/projects
git clone https://github.com/dkumarvaishnav/creative-cloner.git
cd creative-cloner

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .agent/.env
# Edit .agent/.env with your API keys

# Verify setup
python tools/verify_setup.py
```

**You're ready to use!** The skill is at `.agent/skills/creative-cloner/SKILL.md`

### Method 2: Install Just the Skill (Reference Only)

If you only want the documentation for reference:

```bash
# Create global skills directory
mkdir -p ~/.claude/skills

# Clone just the skill folder
cd ~/.claude/skills
git clone https://github.com/dkumarvaishnav/creative-cloner.git
mv creative-cloner/.agent/skills/creative-cloner ./
rm -rf creative-cloner

# Now any Claude Code session can reference:
# ~/.claude/skills/creative-cloner/SKILL.md
```

**Note:** You still need the actual Python tools to execute the workflow!

### Method 3: Fork and Customize

If you want to modify the workflow:

1. **Fork on GitHub:**
   - Go to https://github.com/dkumarvaishnav/creative-cloner
   - Click "Fork" button
   - Creates a copy under your account

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/creative-cloner.git
   cd creative-cloner
   ```

3. **Make your changes:**
   ```bash
   # Modify tools, prompts, or SKILL.md
   git add .
   git commit -m "Customize for my use case"
   git push
   ```

4. **Keep in sync with original:**
   ```bash
   # Add original as upstream
   git remote add upstream https://github.com/dkumarvaishnav/creative-cloner.git

   # Pull latest changes
   git fetch upstream
   git merge upstream/master
   ```

---

## Using in Claude Code

### Step-by-Step: First Time Usage

**1. Prerequisites Check**

Ask Claude:
```
"Check if I have all prerequisites for Creative Cloner"
```

Claude will:
- Run `python tools/verify_setup.py`
- Check Python version, FFmpeg, dependencies, .env file
- Guide you through fixing any issues

**2. Start the Workflow**

Ask Claude:
```
"Help me clone a viral video"
```

Claude will:
1. Check that a video exists in `inputs/` folder
2. Analyze the video (Step 1)
3. Generate prompts (Step 2a)
4. Log to Airtable (Step 2b)
5. **ASK FOR APPROVAL** with cost estimate
6. Generate images in test mode first
7. **ASK FOR APPROVAL** to use production models
8. Generate videos
9. **ASK FOR APPROVAL** for video generation cost
10. Combine final output

### What Claude Knows

Claude reads `.agent/skills/creative-cloner/SKILL.md` and understands:

- ✅ Complete workflow (4 steps, 7 tools)
- ✅ All API endpoints and payloads (Gemini, Kie.ai, Airtable)
- ✅ Cost for each operation
- ✅ When to warn and ask for approval
- ✅ Error handling strategies
- ✅ Test vs production modes
- ✅ Airtable schema requirements

### Advanced Usage

**Generate specific steps:**
```
"Just analyze the video, don't generate anything yet"
"Generate images using test mode only"
"Combine the videos I already have in Airtable"
```

**Cost control:**
```
"What will it cost to generate 3 scenes?"
"Show me dry-run for video generation"
"Use the cheapest models possible"
```

**Troubleshooting:**
```
"Why did image generation fail?"
"Check my Airtable schema"
"Verify FFmpeg is installed correctly"
```

---

## Publishing to Cloud (Future)

When Anthropic releases official cloud skill support, you'll be able to:

### Create Skill Manifest

**File:** `.agent/skills/creative-cloner/skill.json`
```json
{
  "name": "creative-cloner",
  "version": "1.0.0",
  "display_name": "Creative Cloner",
  "description": "Recreate viral videos with your own products or characters using AI",
  "author": "dkumarvaishnav",
  "homepage": "https://github.com/dkumarvaishnav/creative-cloner",
  "license": "MIT",
  "entry_point": "SKILL.md",
  "requirements": {
    "python": ">=3.8",
    "system": ["ffmpeg"],
    "python_packages": [
      "google-genai>=0.3.0",
      "python-dotenv>=1.0.0",
      "pyyaml>=6.0",
      "pyairtable>=2.3.0",
      "requests>=2.28.0"
    ]
  },
  "env_vars": {
    "required": [
      "GEMINI_API_KEY",
      "KIE_API_KEY",
      "AIRTABLE_API_TOKEN",
      "AIRTABLE_BASE_ID"
    ]
  },
  "commands": {
    "verify": "python tools/verify_setup.py",
    "analyze": "python tools/analyze_video.py",
    "generate-prompts": "python tools/generate_prompts.py",
    "log-airtable": "python tools/log_to_airtable.py",
    "generate-images": "python tools/generate_images.py",
    "generate-videos": "python tools/generate_videos.py",
    "combine": "python tools/combine_all.py"
  },
  "tags": ["video", "ai", "generation", "viral", "content-creation"]
}
```

### Publish to Registry

**Future commands (hypothetical):**
```bash
# Login to Claude skill registry
claude skill auth login

# Validate your skill
claude skill validate .agent/skills/creative-cloner

# Publish to registry
claude skill publish creative-cloner --version 1.0.0

# Set as public
claude skill set-visibility creative-cloner public
```

### Install Published Skill

**Users would install with:**
```bash
# Install from registry
claude skill install creative-cloner

# Or install specific version
claude skill install creative-cloner@1.0.0

# Or install from GitHub directly
claude skill install github:dkumarvaishnav/creative-cloner
```

### Invoke with Slash Command

**Future usage:**
```bash
# Start Claude Code
claude-code

# Invoke skill
/creative-cloner
# or
/clone-video
```

---

## Skill Distribution Comparison

### Current State (GitHub)

**Pros:**
- ✅ Available now
- ✅ Full control over code
- ✅ Easy to fork and customize
- ✅ Version control with git
- ✅ Free hosting

**Cons:**
- ❌ Manual installation (clone repo)
- ❌ No automatic updates
- ❌ No discoverability (users must know GitHub URL)
- ❌ Must manually manage dependencies

**Best for:**
- Developers who want to customize
- Teams sharing internally
- Open source contributions

### Future State (Cloud Registry)

**Pros:**
- ✅ One-command install
- ✅ Automatic updates
- ✅ Discoverable (search registry)
- ✅ Dependency resolution
- ✅ Slash command invocation

**Cons:**
- ❌ Not available yet
- ❌ Less control over distribution
- ❌ Possible registry restrictions

**Best for:**
- End users who want simple install
- Wide distribution
- Non-technical users

---

## Recommended Distribution Strategy

### For Now (2025)

**Use GitHub + README:**
1. ✅ Already set up at https://github.com/dkumarvaishnav/creative-cloner
2. Share GitHub URL with users
3. Users clone and follow README.md
4. Claude Code reads SKILL.md for guidance

**To reach more users:**
- Share on social media with demo video
- Write blog post with tutorial
- Create YouTube walkthrough
- Post on Reddit (r/AI, r/VideoEditing, r/SideProject)
- List on awesome-lists (awesome-ai-tools, awesome-video)

### When Cloud Registry Launches

**Migrate to dual distribution:**
1. Keep GitHub repository (for developers)
2. Publish to cloud registry (for end users)
3. Add installation options to README:
   ```markdown
   ## Installation

   **Option 1: Cloud Install (Recommended)**
   ```bash
   claude skill install creative-cloner
   ```

   **Option 2: From Source (Developers)**
   ```bash
   git clone https://github.com/dkumarvaishnav/creative-cloner.git
   ```
   ```

---

## Example: Sharing Your Skill

### Social Media Post

```markdown
🎬 Just launched Creative Cloner - an AI workflow that recreates viral videos!

✨ What it does:
• Analyzes viral videos with Gemini AI
• Generates custom prompts for your product/character
• Creates images with Kie.ai
• Animates into videos with Sora-2
• Combines into final polished output

💰 Cost: ~$1 per 2-scene video
⏱️ Time: ~10 minutes
🤖 Runs as a Claude Code skill

🔗 GitHub: https://github.com/dkumarvaishnav/creative-cloner
📖 Full docs: [link to SKILL.md]

Perfect for:
• Content creators
• Marketing teams
• E-commerce brands
• Indie hackers

Try it out and let me know what you create! 🚀

#AI #VideoCreation #ContentCreation #ClaudeCode #OpenSource
```

### GitHub README Badge

Add to your README:

```markdown
[![Creative Cloner](https://img.shields.io/badge/Claude_Code-Skill-blue)](https://github.com/dkumarvaishnav/creative-cloner)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
```

### Documentation Site (Optional)

Create with GitHub Pages:

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Create docs site
mkdocs new .
# Edit mkdocs.yml and add your docs
mkdocs serve  # Preview locally
mkdocs gh-deploy  # Deploy to GitHub Pages
```

Now your skill has a website at: `https://dkumarvaishnav.github.io/creative-cloner/`

---

## Monetization Options (Future)

If you want to monetize your skill:

### 1. Freemium Model
- Free: Basic skill with 2 scenes
- Paid: Premium version with unlimited scenes, batch processing, custom models

### 2. Service Layer
- Free skill distribution
- Paid managed service (you run the infrastructure)
- Users pay for credits/API access through you

### 3. Consulting
- Free skill
- Paid customization services
- Paid training/workshops

### 4. Marketplace Revenue Share
- If Claude launches skill marketplace
- Revenue share on paid installations
- Similar to VSCode Extension Marketplace

---

## Skill Maintenance

### Keep It Updated

**Monitor for updates:**
- Gemini API changes
- Kie.ai model updates
- Airtable API deprecations
- Python dependency vulnerabilities

**Best practices:**
```bash
# Create a changelog
echo "# Changelog\n\n## [1.0.0] - 2025-01-15\n- Initial release" > CHANGELOG.md

# Tag releases
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Use GitHub Releases
# Go to https://github.com/dkumarvaishnav/creative-cloner/releases
# Create new release with notes
```

### Support Users

**Create issue templates:**

`.github/ISSUE_TEMPLATE/bug_report.md`
```markdown
---
name: Bug Report
about: Report a problem with Creative Cloner
---

**Describe the bug**
A clear description of what happened.

**Setup Information**
- OS: [e.g., Windows 11]
- Python version: [output of `python --version`]
- FFmpeg installed: [yes/no]

**Steps to Reproduce**
1. Run `python tools/analyze_video.py`
2. ...

**Expected vs Actual**
Expected: ...
Actual: ...

**Verification Output**
```
[Paste output of python tools/verify_setup.py]
```
```

**Respond to issues:**
- Check issues regularly
- Provide troubleshooting help
- Update SKILL.md with common solutions

---

## Success Metrics

Track how your skill is being used:

### GitHub Analytics
- Stars (popularity)
- Forks (customization)
- Issues (engagement)
- Traffic (visitors)

### Usage Metrics (Optional)

Add **opt-in** anonymous telemetry:

```python
# tools/analytics.py
def log_usage(event_name, properties=None):
    """Optional anonymous usage tracking (user must opt-in)"""
    if not os.getenv('CREATIVE_CLONER_TELEMETRY', 'false').lower() == 'true':
        return  # Disabled by default

    # Send to your analytics (e.g., PostHog, Mixpanel)
    # NEVER track: API keys, prompts, images, videos, personal data
    # ONLY track: event name, timestamp, version, success/failure
```

**In .env.example:**
```bash
# Optional: Anonymous usage analytics (helps improve the skill)
# Only tracks: command names, success/failure, versions
# Never tracks: your content, prompts, API keys, or personal data
CREATIVE_CLONER_TELEMETRY=false  # Set to 'true' to opt-in
```

---

## Resources

### Learn More
- **Claude Code Documentation:** https://docs.anthropic.com/claude-code
- **GitHub Skills Guide:** https://skills.github.com
- **Open Source Guides:** https://opensource.guide

### Promote Your Skill
- **Show HN (Hacker News):** https://news.ycombinator.com/submit
- **Product Hunt:** https://www.producthunt.com
- **Reddit Communities:** r/SideProject, r/AI, r/VideoEditing
- **Dev.to:** https://dev.to (write a tutorial)
- **Twitter/X:** Use #AI #ClaudeCode #VideoCreation

### Similar Skills (Inspiration)
- Look for other Claude Code skills on GitHub
- Study their README, documentation, and distribution
- Learn from their success

---

## Quick Reference

### Share Your Skill
```bash
# GitHub URL
https://github.com/dkumarvaishnav/creative-cloner

# Quick install for others
git clone https://github.com/dkumarvaishnav/creative-cloner.git
cd creative-cloner
pip install -r requirements.txt
cp .env.example .agent/.env
python tools/verify_setup.py
```

### Use Your Skill
```bash
# In Claude Code
"Help me clone a viral video"

# Or run directly
python tools/analyze_video.py
```

### Update Your Skill
```bash
# After making changes
git add .
git commit -m "Update: <description>"
git push
```

---

**Your Creative Cloner skill is ready to share with the world! 🚀**

Questions? Open an issue: https://github.com/dkumarvaishnav/creative-cloner/issues
