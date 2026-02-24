#!/usr/bin/env python3
"""
Creative Cloner - Video Generator

Generates videos from images using Sora 2 (image-to-video) via Kie.ai API.
Uploads results directly to Airtable.

Usage:
    # Dry run first (recommended)
    python tools/generate_videos.py --dry-run

    # Test with cheap model
    python tools/generate_videos.py --model sora-2 --test-mode

    # Generate for real
    python tools/generate_videos.py --model sora-2

Author: Creative Cloner Team
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv
from pyairtable import Api

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Model configurations
MODELS = {
    'sora-2': {
        'name': 'sora-2-image-to-video',
        'cost': 0.50,  # Approximate cost per video - user should verify
        'max_prompt_length': 10000,
        'default_aspect_ratio': 'landscape',
        'default_duration': '10',  # 10 seconds
        'supports_watermark_removal': True,
        'frame_options': ['10', '15']  # 10s or 15s
    }
}

# API Endpoints
KIE_CREATE_TASK_URL = 'https://api.kie.ai/api/v1/jobs/createTask'
KIE_GET_TASK_URL = 'https://api.kie.ai/api/v1/jobs/recordInfo'


def load_config():
    """Load API keys from .env file"""
    env_path = Path(__file__).parent.parent / '.agent' / '.env'
    load_dotenv(env_path)

    kie_api_key = os.getenv('KIE_API_KEY')
    airtable_token = os.getenv('AIRTABLE_API_TOKEN') or os.getenv('AIRTABLE_API_KEY')
    airtable_base_id = os.getenv('AIRTABLE_BASE_ID')

    if not kie_api_key:
        print("❌ Error: KIE_API_KEY not found in .agent/.env file")
        sys.exit(1)

    if not airtable_token:
        print("❌ Error: AIRTABLE_API_TOKEN not found in .agent/.env file")
        sys.exit(1)

    if not airtable_base_id:
        print("❌ Error: AIRTABLE_BASE_ID not found in .agent/.env file")
        sys.exit(1)

    return {
        'kie_api_key': kie_api_key,
        'airtable_token': airtable_token,
        'airtable_base_id': airtable_base_id
    }


def get_scenes_from_airtable(airtable_token, base_id, project_name):
    """
    Fetch scenes from Airtable that have start_image but no scene_video

    Returns: List of records with their IDs, scene names, image URLs, and video prompts
    """
    print(f"\n📖 Loading scenes from Airtable...")
    print(f"   Project: {project_name}")

    api = Api(airtable_token)
    table = api.table(base_id, 'Scenes')

    # Get all records for this project
    formula = f"{{Project Name}}='{project_name}'"
    all_records = table.all(formula=formula)

    if not all_records:
        return []

    # Filter to only records that have start_image but no scene_video
    scenes = []
    for record in all_records:
        fields = record['fields']
        has_image = 'start_image' in fields and fields['start_image']
        has_video = 'scene_video' in fields and fields['scene_video']

        if has_image and not has_video:
            scenes.append(record)

    print(f"✅ Found {len(scenes)} scene(s) ready for video generation")
    return scenes


def get_image_url_from_record(record):
    """
    Extract the image URL from Airtable attachment field

    Returns: Image URL (str)
    """
    fields = record['fields']
    start_image = fields.get('start_image', [])

    if not start_image or len(start_image) == 0:
        raise Exception("No image found in start_image field")

    # Airtable attachments are a list of objects with 'url' field
    image_url = start_image[0]['url']
    return image_url


def truncate_prompt(prompt, max_length=10000):
    """
    Truncate prompt to fit within character limit while preserving key information
    """
    if len(prompt) <= max_length:
        return prompt

    # Extract key elements (first sentence or two)
    sentences = prompt.split('.')
    truncated = ""
    for sentence in sentences:
        if len(truncated) + len(sentence) + 1 <= max_length - 50:  # Leave room for ending
            truncated += sentence + "."
        else:
            break

    # If still empty or too short, just truncate at max_length
    if not truncated or len(truncated) < 50:
        truncated = prompt[:max_length-3] + "..."

    return truncated.strip()


def create_video_generation_task(prompt, image_url, model_name, api_key, model_config,
                                   aspect_ratio='landscape', n_frames='10', remove_watermark=True):
    """
    Create video generation task on Kie.ai using Sora 2

    Returns: taskId (str)
    """
    print(f"\n🎬 Creating video generation task...")
    print(f"   Model: {model_name}")
    print(f"   Image URL: {image_url[:60]}...")
    print(f"   Aspect Ratio: {aspect_ratio}")
    print(f"   Duration: {n_frames}s")

    # Truncate prompt if needed for model limits
    max_prompt_length = model_config.get('max_prompt_length', 10000)
    original_length = len(prompt)
    if original_length > max_prompt_length:
        prompt = truncate_prompt(prompt, max_prompt_length)
        print(f"   ⚠️  Prompt truncated: {original_length} → {len(prompt)} chars")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Build payload for Sora 2
    payload = {
        'model': model_name,
        'input': {
            'prompt': prompt,
            'image_urls': [image_url],
            'aspect_ratio': aspect_ratio,
            'n_frames': str(n_frames),
            'remove_watermark': remove_watermark,
            'upload_method': 's3'
        }
    }

    print(f"   Prompt length: {len(prompt)} chars")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            KIE_CREATE_TASK_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"   Response status: {response.status_code}")

        if response.status_code == 402:
            raise Exception("❌ Insufficient credits! Please add credits to your Kie.ai account.")
        elif response.status_code == 422:
            raise Exception(f"❌ Invalid parameters: {response.text}")
        elif response.status_code == 429:
            raise Exception("❌ Rate limited! Please wait a moment and try again.")
        elif response.status_code != 200:
            raise Exception(f"Task creation failed: {response.status_code} - {response.text}")

        result = response.json()
        print(f"   Response body: {json.dumps(result, indent=2)}")

        if not result:
            raise Exception("Empty response from API")

        data = result.get('data', {})
        if not data:
            raise Exception(f"No 'data' field in response: {result}")

        task_id = data.get('taskId')
        if not task_id:
            raise Exception(f"No taskId in response data: {data}")

        print(f"✅ Task created: {task_id}")
        return task_id

    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")
    except Exception as e:
        raise Exception(f"Failed to create task: {e}")


def poll_task_status(task_id, api_key, max_wait=900):
    """
    Poll task status until completion
    Video generation typically takes 2-4 minutes

    Returns: List of result URLs
    """
    print(f"\n⏳ Polling task status...")
    print(f"   Task ID: {task_id}")
    print(f"   Note: Video generation can take 2-4 minutes")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < max_wait:
        poll_count += 1
        elapsed = int(time.time() - start_time)

        try:
            response = requests.get(
                f"{KIE_GET_TASK_URL}?taskId={task_id}",
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                print(f"   ⚠️  Poll failed: {response.status_code}")
                time.sleep(5)
                continue

            result = response.json()
            data = result.get('data', {})
            state = data.get('state')

            print(f"   [{elapsed}s] Poll #{poll_count}: state={state}")

            if state == 'success':
                # Parse resultJson
                result_json = data.get('resultJson', '{}')
                if isinstance(result_json, str):
                    result_data = json.loads(result_json)
                else:
                    result_data = result_json

                result_urls = result_data.get('resultUrls', [])
                print(f"✅ Generation complete! Got {len(result_urls)} result(s)")
                return result_urls

            elif state == 'fail':
                fail_msg = data.get('failMsg', 'Unknown error')
                fail_code = data.get('failCode', 'N/A')
                raise Exception(f"Generation failed: [{fail_code}] {fail_msg}")

            # Smart polling interval based on elapsed time
            if elapsed < 60:
                time.sleep(10)  # Poll every 10s for first minute
            elif elapsed < 180:
                time.sleep(15)  # Poll every 15s for next 2 minutes
            else:
                time.sleep(30)  # Poll every 30s after 3 minutes

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️  Network error: {e}")
            time.sleep(5)
            continue
        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse error: {e}")
            time.sleep(5)
            continue

    raise Exception(f"Task did not complete within {max_wait}s timeout")


def update_airtable_record(record_id, video_url, airtable_token, base_id):
    """
    Update Airtable record with generated video URL

    Airtable automatically downloads the file from the URL
    """
    print(f"\n📊 Updating Airtable record: {record_id}")
    print(f"   Field: scene_video")
    print(f"   Video URL: {video_url[:60]}...")

    api = Api(airtable_token)
    table = api.table(base_id, 'Scenes')

    try:
        # Update with attachment URL
        # Airtable expects: {'field_name': [{'url': 'http://...'}]}
        table.update(record_id, {
            'scene_video': [{'url': video_url}]
        })
        print(f"✅ Airtable updated successfully")
    except Exception as e:
        raise Exception(f"Failed to update Airtable: {e}")


def download_video(video_url, output_path):
    """
    Download video from URL to local file

    Returns: Local file path
    """
    print(f"\n💾 Downloading video...")
    print(f"   From: {video_url[:60]}...")
    print(f"   To: {output_path}")

    try:
        response = requests.get(video_url, stream=True, timeout=120)
        response.raise_for_status()

        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Download in chunks
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = output_path.stat().st_size / (1024 * 1024)  # MB
        print(f"✅ Downloaded: {file_size:.2f} MB")
        return output_path

    except Exception as e:
        raise Exception(f"Failed to download video: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate videos from images using Sora 2 via Kie.ai API'
    )
    parser.add_argument(
        '--model',
        choices=['sora-2'],
        default='sora-2',
        help='Model to use for video generation (default: sora-2)'
    )
    parser.add_argument(
        '--project-name',
        default='Creative Cloner Project',
        help='Project name in Airtable (default: Creative Cloner Project)'
    )
    parser.add_argument(
        '--aspect-ratio',
        choices=['portrait', 'landscape'],
        default=None,
        help='Video aspect ratio (default: landscape)'
    )
    parser.add_argument(
        '--duration',
        choices=['10', '15'],
        default='10',
        help='Video duration in seconds (default: 10)'
    )
    parser.add_argument(
        '--remove-watermark',
        action='store_true',
        default=True,
        help='Remove watermark from generated videos (default: True)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually generating videos'
    )
    parser.add_argument(
        '--skip-approval',
        action='store_true',
        help='Skip cost approval prompt (use with caution!)'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Test mode: use simple test data instead of real Airtable data'
    )
    parser.add_argument(
        '--skip-download',
        action='store_true',
        help='Skip downloading videos locally (only update Airtable)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🎬 Creative Cloner - Video Generator")
    print("=" * 80)

    # Load configuration
    config = load_config()
    print("✅ Configuration loaded")

    # Get model config
    model_config = MODELS[args.model]
    print(f"\n📋 Model: {model_config['name']}")
    print(f"   Cost: ${model_config['cost']} per video (estimated)")
    print(f"   Duration: {args.duration}s")

    # Load scenes from Airtable (or use test mode)
    if args.test_mode:
        print("\n🧪 TEST MODE - Using test data")
        print("   Note: In test mode, you need to manually create a test record")
        print("   with a start_image already uploaded to test the video workflow.")
        print("\n   Please run in normal mode with a project that has images.")
        sys.exit(1)
    else:
        scenes = get_scenes_from_airtable(
            config['airtable_token'],
            config['airtable_base_id'],
            args.project_name
        )

        if not scenes:
            print("❌ No scenes ready for video generation!")
            print("   Make sure scenes have start_image but no scene_video")
            print("   Run generate_images.py first to create images")
            sys.exit(1)

    # Calculate total cost
    total_cost = len(scenes) * model_config['cost']
    print(f"\n💰 Cost Estimate:")
    print(f"   {len(scenes)} videos × ${model_config['cost']} = ${total_cost:.2f}")

    # Get user approval unless skipped or dry-run
    if not args.dry_run and not args.skip_approval:
        print(f"\n⚠️  This will generate {len(scenes)} videos at ${model_config['cost']} each = ${total_cost:.2f} total")
        print(f"   Video generation takes 2-4 minutes per video")
        response = input("Ready to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled by user")
            sys.exit(0)

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No actual API calls will be made")
        print("\n" + "=" * 80)
        for i, record in enumerate(scenes, 1):
            fields = record['fields']
            image_url = get_image_url_from_record(record)
            print(f"\nScene {i}:")
            print(f"  ID: {record['id']}")
            print(f"  Name: {fields.get('scene', 'N/A')}")
            print(f"  Image URL: {image_url[:60]}...")
            print(f"  Video Prompt: {fields.get('video_prompt', 'N/A')[:100]}...")
            print(f"  Would generate with model: {args.model}")
            print(f"  Would update Airtable field: scene_video")
            if not args.skip_download:
                print(f"  Would download to: outputs/")
        print("\n" + "=" * 80)
        print("✅ Dry run complete")
        return

    # Generate videos
    print("\n" + "=" * 80)
    print(f"🚀 Starting generation for {len(scenes)} scene(s)")
    print("=" * 80)

    success_count = 0
    fail_count = 0
    actual_cost = 0

    outputs_dir = Path(__file__).parent.parent / 'outputs'

    for i, record in enumerate(scenes, 1):
        print("\n" + "-" * 80)
        fields = record['fields']
        scene_name = fields.get('scene', f'Scene {i}')
        print(f"Scene {i}/{len(scenes)}: {scene_name}")
        print("-" * 80)

        # Get image URL and video prompt
        try:
            image_url = get_image_url_from_record(record)
            video_prompt = fields.get('video_prompt', '')

            if not video_prompt:
                print("⚠️  No video_prompt found, skipping...")
                continue

        except Exception as e:
            print(f"❌ Error getting scene data: {e}")
            fail_count += 1
            continue

        try:
            # Create generation task
            task_id = create_video_generation_task(
                prompt=video_prompt,
                image_url=image_url,
                model_name=model_config['name'],
                api_key=config['kie_api_key'],
                model_config=model_config,
                aspect_ratio=args.aspect_ratio or model_config['default_aspect_ratio'],
                n_frames=args.duration,
                remove_watermark=args.remove_watermark
            )

            # Poll for completion
            result_urls = poll_task_status(task_id, config['kie_api_key'])

            if not result_urls:
                raise Exception("No result URLs returned")

            video_url = result_urls[0]

            # Update Airtable
            update_airtable_record(
                record['id'],
                video_url,
                config['airtable_token'],
                config['airtable_base_id']
            )

            # Download video locally (unless skipped)
            if not args.skip_download:
                video_filename = f"scene_{i}_{scene_name.replace(' ', '_')[:30]}.mp4"
                video_path = outputs_dir / video_filename
                download_video(video_url, video_path)

            success_count += 1
            actual_cost += model_config['cost']

            # Rate limit protection - wait between videos
            if i < len(scenes):
                print(f"\n⏸️  Waiting 5s before next video...")
                time.sleep(5)

        except Exception as e:
            print(f"❌ Error generating video: {e}")
            fail_count += 1
            continue

    # Final summary
    print("\n" + "=" * 80)
    print("📊 GENERATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"💰 Actual cost: ${actual_cost:.2f}")
    print("=" * 80)

    print("\n✨ Done! Check your Airtable base to see the generated videos.")
    print(f"   Base URL: https://airtable.com/{config['airtable_base_id']}")
    if not args.skip_download:
        print(f"   Videos saved to: {outputs_dir}")


if __name__ == '__main__':
    main()
