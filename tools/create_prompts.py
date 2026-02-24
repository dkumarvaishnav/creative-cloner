#!/usr/bin/env python3
"""
Prompt Creator for Creative Cloner

Takes a video analysis YAML and a reference image, then creates:
1. IMAGE PROMPTS - for generating static frames with NanoBanana Pro
2. VIDEO PROMPTS - for animating frames with Kling 2.6

Maintains original environment, lighting, camera angles while
replacing the subject with the new product/character.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import yaml
from google import genai
from google.genai import types

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


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


def load_analysis(analysis_path):
    """Load video analysis from YAML file"""
    print(f"📖 Loading video analysis from: {analysis_path}")

    if not os.path.exists(analysis_path):
        print(f"❌ Error: Analysis file not found: {analysis_path}")
        sys.exit(1)

    with open(analysis_path, 'r', encoding='utf-8') as f:
        analysis = yaml.safe_load(f)

    print(f"✅ Loaded analysis with {analysis['video_analysis']['total_scenes']} scenes")
    return analysis


def upload_reference_image(image_path, client):
    """Upload reference image to Gemini"""
    print(f"\n📤 Uploading reference image: {image_path}")

    if not os.path.exists(image_path):
        print(f"❌ Error: Reference image not found: {image_path}")
        sys.exit(1)

    # Detect mime type
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type or not mime_type.startswith('image/'):
        mime_type = 'image/jpeg'

    print(f"   Detected MIME type: {mime_type}")

    # Upload the image file
    with open(image_path, 'rb') as image_data:
        image_file = client.files.upload(
            file=image_data,
            config=types.UploadFileConfig(mime_type=mime_type)
        )

    print(f"✅ Upload complete: {image_file.name}")
    return image_file


def describe_reference(image_file, client):
    """Describe the reference product/character using Gemini"""
    print("\n🔍 Analyzing reference image...")

    prompt = """
    Describe this product/character in detail for use in image generation prompts.

    Focus on:
    - What is it? (person, product, character, mascot, etc.)
    - Key visual features (colors, shape, distinctive elements)
    - Style (realistic, cartoon, 3D render, etc.)
    - Any text, logos, or branding
    - Size/scale context if relevant

    Be specific and descriptive but concise (2-3 sentences).
    This description will be used to generate images of this subject in different scenes.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_uri(file_uri=image_file.uri, mime_type=image_file.mime_type),
            prompt
        ]
    )

    description = response.text.strip()
    print(f"✅ Reference description: {description}")
    return description


def create_prompts(analysis, subject_description):
    """Create image and video prompts for each scene"""
    print("\n✨ Creating prompts for each scene...")

    prompts = []
    scenes = analysis['video_analysis']['scenes']

    for scene in scenes:
        scene_num = scene['scene_number']
        print(f"\n   Scene {scene_num}:")

        # Create IMAGE PROMPT for NanoBanana Pro
        image_prompt = f"""{subject_description}

Setting: {scene['environment']}
Lighting: {scene['lighting']}
Camera: {scene['camera']}

The subject is in this position/pose: {scene['action'].split('.')[0]}.

Style: Photorealistic, high quality, professional photography
Details: Sharp focus, natural colors, {scene['lighting'].lower()}"""

        print(f"      ✓ Image prompt created")

        # Create VIDEO PROMPT for Kling 2.6
        video_prompt = f"""Camera Type: {scene['camera']}

Main Movement: {subject_description} {scene['action']}

Setting: {scene['environment']}
Lighting: {scene['lighting']}

Motion details: {scene['action']}
Duration: {scene['duration']} seconds

Style: Smooth, natural motion, high quality video, realistic physics"""

        print(f"      ✓ Video prompt created")

        prompts.append({
            'scene_number': scene_num,
            'scene_description': scene['description'],
            'duration': scene['duration'],
            'image_prompt': image_prompt.strip(),
            'video_prompt': video_prompt.strip()
        })

    print(f"\n✅ Created {len(prompts)} prompt pairs")
    return prompts


def save_prompts(prompts, output_path, analysis):
    """Save prompts to YAML file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_data = {
        'metadata': {
            'total_scenes': len(prompts),
            'total_duration': analysis['video_analysis']['overall_duration'],
            'music_sound': analysis['video_analysis']['music_sound']
        },
        'prompts': prompts
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"\n💾 Prompts saved to: {output_path}")


def print_prompts(prompts):
    """Print prompts to console in readable format"""
    print("\n" + "=" * 80)
    print("📋 GENERATED PROMPTS")
    print("=" * 80)

    for p in prompts:
        print(f"\n{'─' * 80}")
        print(f"SCENE {p['scene_number']} ({p['duration']} seconds)")
        print(f"Original: {p['scene_description']}")
        print(f"{'─' * 80}")

        print(f"\n📸 IMAGE PROMPT (NanoBanana Pro):")
        print("─" * 40)
        print(p['image_prompt'])

        print(f"\n\n🎬 VIDEO PROMPT (Kling 2.6):")
        print("─" * 40)
        print(p['video_prompt'])
        print()

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Create image and video prompts from video analysis and reference image'
    )
    parser.add_argument(
        'reference_image',
        help='Path to reference image of your product/character'
    )
    parser.add_argument(
        '-a', '--analysis',
        help='Path to video analysis YAML (default: outputs/analysis.yaml)',
        default='outputs/analysis.yaml'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output path for prompts YAML (default: outputs/prompts.yaml)',
        default='outputs/prompts.yaml'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🎨 Creative Cloner - Prompt Creator")
    print("=" * 80)

    # Load API key and configure Gemini
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    print("✅ Gemini API configured")

    # Load video analysis
    analysis = load_analysis(args.analysis)

    # Upload and analyze reference image
    image_file = upload_reference_image(args.reference_image, client)
    subject_description = describe_reference(image_file, client)

    # Create prompts
    prompts = create_prompts(analysis, subject_description)

    # Save prompts
    save_prompts(prompts, args.output, analysis)

    # Print prompts
    print_prompts(prompts)

    # Cleanup
    client.files.delete(name=image_file.name)
    print("\n🗑️  Temporary files cleaned up")
    print("\n✨ Done! Prompts ready for image and video generation.")


if __name__ == '__main__':
    main()
