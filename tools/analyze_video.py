#!/usr/bin/env python3
"""
Video Analysis Script using Gemini API and SEALCaM Framework

Analyzes videos scene-by-scene and extracts:
- Scene description
- Subject (main focus)
- Environment/setting
- Action (motion/activity)
- Lighting style
- Camera angle/movement
- Approximate duration
- Music/sound description

Output: YAML format for easy parsing
"""

import os
import sys
import time
import argparse
import mimetypes
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
import yaml

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# SEALCaM Analysis Prompt
ANALYSIS_PROMPT = """
Analyze this video using the SEALCaM framework (Scene, Environment, Action, Lighting, Camera, Music).

Break down the video into distinct scenes and for each scene provide:

1. **Scene Number**: Sequential numbering
2. **Scene Description**: Brief overview of what's happening
3. **Subject**: The main focus (person, object, character)
4. **Environment**: Setting/location/background
5. **Action**: What motion or activity is occurring
6. **Lighting**: Lighting style (natural, studio, dramatic, soft, etc.)
7. **Camera**: Camera angle and movement (static, pan, zoom, tracking, POV, etc.)
8. **Duration**: Approximate duration of the scene in seconds

Also provide:
- **Overall Music/Sound**: Description of background music, sound effects, or audio style

Format your response as a structured analysis that can be easily parsed into YAML.
Use clear section headers and consistent formatting.

Example format:
---
video_analysis:
  overall_duration: X seconds
  total_scenes: N
  music_sound: "Description of audio/music"

  scenes:
    - scene_number: 1
      description: "..."
      subject: "..."
      environment: "..."
      action: "..."
      lighting: "..."
      camera: "..."
      duration: X

    - scene_number: 2
      description: "..."
      ...

Now analyze the provided video.
"""


def load_api_key():
    """Load Gemini API key from .env file"""
    env_path = Path(__file__).parent.parent / '.agent' / '.env'
    load_dotenv(env_path)

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .agent/.env file")
        print(f"   Please add your API key to: {env_path}")
        sys.exit(1)

    return api_key


def upload_video(video_path, client):
    """Upload video to Gemini and wait for processing"""
    print(f"📤 Uploading video: {video_path}")

    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)

    # Detect mime type
    mime_type, _ = mimetypes.guess_type(video_path)
    if not mime_type:
        # Default to mp4 if detection fails
        mime_type = 'video/mp4'

    print(f"   Detected MIME type: {mime_type}")

    # Upload the video file
    with open(video_path, 'rb') as video_data:
        upload_response = client.files.upload(
            file=video_data,
            config=types.UploadFileConfig(mime_type=mime_type)
        )

    print(f"✅ Upload complete: {upload_response.name}")

    # Wait for video processing
    print("⏳ Processing video...")
    video_file = upload_response
    while video_file.state == types.FileState.PROCESSING:
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)

    if video_file.state == types.FileState.FAILED:
        print("❌ Video processing failed")
        sys.exit(1)

    print("✅ Video processing complete")
    return video_file


def analyze_video(video_file, client):
    """Analyze video using Gemini with SEALCaM framework"""
    print("\n🔍 Analyzing video with SEALCaM framework...")

    # Generate analysis using Gemini 2.5 Flash (available on free tier with video support)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_uri(file_uri=video_file.uri, mime_type=video_file.mime_type),
            ANALYSIS_PROMPT
        ]
    )

    print("✅ Analysis complete")
    return response.text


def parse_to_yaml(analysis_text):
    """Parse the analysis text to YAML format"""
    print("\n📝 Formatting analysis as YAML...")

    # Check if the response contains YAML in a code block
    if '```yaml' in analysis_text or '```yml' in analysis_text:
        # Extract YAML from code block
        import re
        match = re.search(r'```ya?ml\n(.*?)\n```', analysis_text, re.DOTALL)
        if match:
            yaml_text = match.group(1).strip()
            try:
                # Validate it's proper YAML
                yaml.safe_load(yaml_text)
                return yaml_text
            except yaml.YAMLError as e:
                print(f"⚠️  Warning: YAML validation failed: {e}")

    # Check if the response already contains YAML
    if '---' in analysis_text or 'video_analysis:' in analysis_text:
        # Try to extract YAML portion
        try:
            # Find the YAML section
            yaml_start = analysis_text.find('---')
            if yaml_start != -1:
                yaml_text = analysis_text[yaml_start:]
            else:
                yaml_text = analysis_text

            # Validate it's proper YAML
            yaml.safe_load(yaml_text)
            return yaml_text
        except yaml.YAMLError:
            pass

    # If not in YAML format, wrap the raw analysis
    yaml_output = {
        'video_analysis': {
            'raw_analysis': analysis_text,
            'note': 'Analysis returned in text format - may need manual parsing'
        }
    }

    return yaml.dump(yaml_output, default_flow_style=False, sort_keys=False)


def save_analysis(yaml_content, output_path):
    """Save analysis to file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    print(f"💾 Analysis saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze video using Gemini API and SEALCaM framework'
    )
    parser.add_argument(
        'video_path',
        help='Path to the video file to analyze'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output path for YAML analysis (default: outputs/analysis.yaml)',
        default='outputs/analysis.yaml'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🎬 Creative Cloner - Video Analysis")
    print("=" * 60)

    # Load API key and configure Gemini
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    print("✅ Gemini API configured\n")

    # Upload and process video
    video_file = upload_video(args.video_path, client)

    # Analyze video
    analysis = analyze_video(video_file, client)

    # Convert to YAML
    yaml_content = parse_to_yaml(analysis)

    # Save to file
    save_analysis(yaml_content, args.output)

    # Also print to console
    print("\n" + "=" * 60)
    print("📋 ANALYSIS RESULTS")
    print("=" * 60)
    print(yaml_content)
    print("=" * 60)
    print("\n✨ Done! Analysis complete.")

    # Cleanup
    client.files.delete(name=video_file.name)
    print("🗑️  Temporary files cleaned up")


if __name__ == '__main__':
    main()
