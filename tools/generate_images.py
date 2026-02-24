#!/usr/bin/env python3
"""
Image Generator for Creative Cloner using Kie.ai API

Generates images from prompts and uploads them directly to Airtable.
Supports multiple models with cost tracking and approval workflow.

Models:
- z-image: $0.004/image (recommended for testing)
- nano-banana-pro: $0.09/image (production quality)
"""

import os
import sys
import time
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
import requests
from pyairtable import Api
from pyairtable.utils import attachment

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Model configurations
MODELS = {
    'z-image': {
        'name': 'z-image',
        'cost': 0.004,
        'supports_image_input': False,  # z-image does NOT support reference images
        'supports_resolution': False,   # z-image does NOT support resolution parameter
        'max_prompt_length': 1000,      # z-image has 1000 character limit
        'default_aspect_ratio': '1:1'
    },
    'nano-banana-pro': {
        'name': 'nano-banana-pro',
        'cost': 0.09,
        'supports_image_input': True,
        'supports_resolution': True,
        'max_prompt_length': 10000,     # Much higher limit
        'default_resolution': '1K',
        'default_aspect_ratio': '1:1'
    }
}

# API Endpoints
KIE_FILE_UPLOAD_URL = 'https://kieai.redpandaai.co/api/file-stream-upload'
KIE_CREATE_TASK_URL = 'https://api.kie.ai/api/v1/jobs/createTask'
KIE_TASK_STATUS_URL = 'https://api.kie.ai/api/v1/jobs/recordInfo'


def load_config():
    """Load API keys from .env file"""
    env_path = Path(__file__).parent.parent / '.agent' / '.env'
    load_dotenv(env_path)

    config = {
        'kie_api_key': os.getenv('KIE_API_KEY'),
        'airtable_token': os.getenv('AIRTABLE_API_TOKEN') or os.getenv('AIRTABLE_API_KEY'),
        'airtable_base_id': os.getenv('AIRTABLE_BASE_ID')
    }

    # Validate required keys
    missing = [k for k, v in config.items() if not v]
    if missing:
        print(f"❌ Error: Missing environment variables: {', '.join(missing)}")
        print(f"   Please add them to: {env_path}")
        sys.exit(1)

    return config


def upload_reference_image_to_kie(image_path, api_key):
    """
    Upload reference image to Kie.ai file hosting

    Returns: fileUrl (str) - Public URL of uploaded file
    """
    print(f"📤 Uploading reference image to Kie.ai: {image_path}")

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Reference image not found: {image_path}")

    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    with open(image_path, 'rb') as f:
        files = {
            'file': (os.path.basename(image_path), f, 'image/jpeg')
        }
        data = {
            'uploadPath': 'creative-cloner',
            'fileName': os.path.basename(image_path)
        }

        response = requests.post(
            KIE_FILE_UPLOAD_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=60
        )

    if response.status_code != 200:
        raise Exception(f"File upload failed: {response.status_code} - {response.text}")

    result = response.json()
    data = result.get('data', {})

    # Kie.ai returns 'downloadUrl', not 'fileUrl'
    file_url = data.get('downloadUrl') or data.get('fileUrl')

    if not file_url:
        raise Exception(f"No downloadUrl/fileUrl in response: {result}")

    print(f"✅ Uploaded: {file_url}")
    return file_url


def truncate_prompt(prompt, max_length=1000):
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


def create_image_generation_task(prompt, model_name, api_key, model_config, reference_image_url=None,
                                   aspect_ratio='1:1', resolution='1K'):
    """
    Create image generation task on Kie.ai

    Returns: taskId (str)
    """
    print(f"\n🎨 Creating image generation task...")
    print(f"   Model: {model_name}")
    print(f"   Aspect Ratio: {aspect_ratio}")

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

    # Build payload based on model
    payload = {
        'model': model_name,
        'input': {
            'prompt': prompt,
            'aspect_ratio': aspect_ratio
        }
    }

    # Add model-specific parameters
    if model_name == 'nano-banana-pro':
        if model_config.get('supports_resolution'):
            payload['input']['resolution'] = resolution
            print(f"   Resolution: {resolution}")
        payload['input']['output_format'] = 'png'
        if reference_image_url and model_config.get('supports_image_input'):
            payload['input']['image_input'] = [reference_image_url]
            print(f"   Reference image: ✓")

    elif model_name == 'z-image':
        # z-image only supports prompt and aspect_ratio
        # No resolution, no image_input, no other parameters
        print(f"   Note: z-image doesn't support reference images or resolution")
        if reference_image_url:
            print(f"   ⚠️  Reference image ignored (not supported by z-image)")

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
        # Re-raise with more context
        raise Exception(f"Failed to create task: {e}")


def poll_task_status(task_id, api_key, max_wait=600):
    """
    Poll task status until completion

    Returns: List of result URLs
    """
    print(f"\n⏳ Polling task status: {task_id}")

    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < max_wait:
        poll_count += 1

        try:
            response = requests.get(
                f"{KIE_TASK_STATUS_URL}?taskId={task_id}",
                headers=headers,
                timeout=30
            )

            if response.status_code != 200:
                print(f"⚠️  Poll attempt {poll_count} failed: {response.status_code}")
                time.sleep(5)
                continue

            result = response.json()
            data = result.get('data', {})
            state = data.get('state')

            elapsed = int(time.time() - start_time)
            print(f"   [{elapsed}s] Poll #{poll_count}: state={state}")

            if state == 'success':
                # Parse resultJson (it's a JSON string!)
                result_json_str = data.get('resultJson', '{}')
                result_json = json.loads(result_json_str)
                result_urls = result_json.get('resultUrls', [])

                if not result_urls:
                    raise Exception(f"No resultUrls in response: {result_json}")

                print(f"✅ Generation complete! Got {len(result_urls)} result(s)")
                return result_urls

            elif state == 'fail':
                fail_msg = data.get('failMsg', 'Unknown error')
                fail_code = data.get('failCode', 'N/A')
                raise Exception(f"Generation failed [{fail_code}]: {fail_msg}")

            elif state in ['waiting', 'queuing', 'generating']:
                # Smart polling interval
                if elapsed < 30:
                    time.sleep(3)
                elif elapsed < 120:
                    time.sleep(5)
                else:
                    time.sleep(10)
            else:
                print(f"⚠️  Unknown state: {state}")
                time.sleep(5)

        except requests.exceptions.RequestException as e:
            print(f"⚠️  Network error during poll: {e}")
            time.sleep(5)

    raise TimeoutError(f"Task did not complete within {max_wait} seconds")


def update_airtable_with_image(airtable_token, base_id, record_id, image_url, field_name='start_image'):
    """
    Update Airtable record with generated image URL
    Airtable will automatically download and host the file
    """
    print(f"\n📊 Updating Airtable record: {record_id}")
    print(f"   Field: {field_name}")
    print(f"   Image URL: {image_url}")

    api = Api(airtable_token)
    table = api.table(base_id, 'Scenes')

    try:
        # Use attachment utility to format URL correctly
        table.update(record_id, {
            field_name: [attachment(image_url)]
        })

        print(f"✅ Airtable updated successfully")

    except Exception as e:
        raise Exception(f"Failed to update Airtable: {e}")


def get_scenes_from_airtable(airtable_token, base_id, project_name='Creative Cloner Project'):
    """Get all scenes from Airtable for the project"""
    print(f"\n📖 Loading scenes from Airtable...")
    print(f"   Project: {project_name}")

    api = Api(airtable_token)
    table = api.table(base_id, 'Scenes')

    formula = f"{{Project Name}}='{project_name}'"
    records = table.all(formula=formula)

    print(f"✅ Found {len(records)} scene(s)")
    return records


def main():
    parser = argparse.ArgumentParser(
        description='Generate images using Kie.ai and upload to Airtable',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Models:
  z-image          $0.004/image (recommended for testing)
  nano-banana-pro  $0.09/image  (production quality)

Example:
  python generate_images.py --model z-image --dry-run
  python generate_images.py --model nano-banana-pro --aspect-ratio 9:16
        """
    )
    parser.add_argument(
        '-m', '--model',
        choices=['z-image', 'nano-banana-pro'],
        default='z-image',
        help='Model to use for generation (default: z-image)'
    )
    parser.add_argument(
        '-r', '--reference-image',
        help='Path to reference image (default: auto-detect from inputs/)',
        default=None
    )
    parser.add_argument(
        '--aspect-ratio',
        help='Aspect ratio for generated images (default: from prompts or 1:1)',
        default=None
    )
    parser.add_argument(
        '--resolution',
        choices=['1K', '2K', '4K'],
        default='1K',
        help='Image resolution (default: 1K for testing)'
    )
    parser.add_argument(
        '--project-name',
        default='Creative Cloner Project',
        help='Project name in Airtable (default: Creative Cloner Project)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually generating images'
    )
    parser.add_argument(
        '--skip-approval',
        action='store_true',
        help='Skip cost approval prompt (use with caution!)'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Test mode: use a simple short prompt instead of Airtable prompts'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🎨 Creative Cloner - Image Generator")
    print("=" * 80)

    # Load configuration
    config = load_config()
    print("✅ Configuration loaded")

    # Get model config
    model_config = MODELS[args.model]
    print(f"\n📋 Model: {model_config['name']}")
    print(f"   Cost: ${model_config['cost']} per image")

    # Load scenes from Airtable (or use test mode)
    if args.test_mode:
        print("\n🧪 TEST MODE - Creating simple test prompt")
        # Create a simple test record
        api = Api(config['airtable_token'])
        table = api.table(config['airtable_base_id'], 'Scenes')

        # Create or update test record
        test_prompt = "A young man smiling at the camera, indoor setting, natural lighting"

        # Check if test record exists
        formula = f"{{Project Name}}='TEST-{args.project_name}'"
        existing = table.all(formula=formula)

        if existing:
            print(f"   Found existing test record, using it")
            scenes = existing
        else:
            print(f"   Creating new test record")
            test_record = table.create({
                'Project Name': f'TEST-{args.project_name}',
                'scene': 'TEST - Simple workflow test',
                'start_image_prompt': test_prompt,
                'video_prompt': 'Test video prompt'
            })
            scenes = [test_record]

        print(f"   Test prompt: {test_prompt}")
        print(f"   Prompt length: {len(test_prompt)} chars")
    else:
        scenes = get_scenes_from_airtable(
            config['airtable_token'],
            config['airtable_base_id'],
            args.project_name
        )

        if not scenes:
            print("❌ No scenes found in Airtable!")
            print("   Run log_to_airtable.py first to create scene records")
            sys.exit(1)

    # Calculate total cost
    total_cost = len(scenes) * model_config['cost']
    print(f"\n💰 Cost Estimate:")
    print(f"   {len(scenes)} images × ${model_config['cost']} = ${total_cost:.2f}")

    # Get user approval unless skipped or dry-run
    if not args.dry_run and not args.skip_approval:
        print(f"\n⚠️  This will generate {len(scenes)} images at ${model_config['cost']} each = ${total_cost:.2f} total")
        response = input("Ready to proceed? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled by user")
            sys.exit(0)

    # Find reference image (skip in test mode for z-image)
    reference_image_path = args.reference_image
    if not reference_image_path and not args.test_mode:
        # Auto-detect from inputs/ folder
        inputs_dir = Path(__file__).parent.parent / 'inputs'
        image_files = list(inputs_dir.glob('*.jpg')) + list(inputs_dir.glob('*.png')) + list(inputs_dir.glob('*.jpeg'))
        image_files = [f for f in image_files if not f.name.endswith('.mp4')]

        if image_files:
            reference_image_path = str(image_files[0])
            print(f"\n📸 Auto-detected reference image: {reference_image_path}")
        else:
            print("\n⚠️  No reference image found in inputs/ folder")
            print("   Generating without reference image")

    if args.test_mode:
        print(f"\n🧪 Test mode: Skipping reference image (z-image doesn't support it anyway)")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No actual API calls will be made")
        print("\n" + "=" * 80)
        for i, record in enumerate(scenes, 1):
            fields = record['fields']
            print(f"\nScene {i}:")
            print(f"  ID: {record['id']}")
            print(f"  Name: {fields.get('scene', 'N/A')}")
            print(f"  Prompt: {fields.get('start_image_prompt', 'N/A')[:100]}...")
            if reference_image_path:
                print(f"  Would upload reference: {reference_image_path}")
            print(f"  Would generate with model: {args.model}")
            print(f"  Would update Airtable field: start_image")
        print("\n" + "=" * 80)
        print("✅ Dry run complete")
        return

    # Upload reference image to Kie if provided (skip in test mode)
    reference_image_url = None
    if reference_image_path and not args.test_mode:
        try:
            reference_image_url = upload_reference_image_to_kie(
                reference_image_path,
                config['kie_api_key']
            )
        except Exception as e:
            print(f"❌ Failed to upload reference image: {e}")
            print("   Continuing without reference image...")

    # Process each scene
    print(f"\n{'=' * 80}")
    print(f"🚀 Starting generation for {len(scenes)} scene(s)")
    print(f"{'=' * 80}")

    successful = 0
    failed = 0

    for i, record in enumerate(scenes, 1):
        record_id = record['id']
        fields = record['fields']
        scene_name = fields.get('scene', f'Scene {i}')
        prompt = fields.get('start_image_prompt', '')

        print(f"\n{'─' * 80}")
        print(f"Scene {i}/{len(scenes)}: {scene_name}")
        print(f"{'─' * 80}")

        if not prompt:
            print("⚠️  No image prompt found, skipping...")
            failed += 1
            continue

        try:
            # Create generation task
            task_id = create_image_generation_task(
                prompt=prompt,
                model_name=args.model,
                api_key=config['kie_api_key'],
                model_config=model_config,
                reference_image_url=reference_image_url,
                aspect_ratio=args.aspect_ratio or model_config['default_aspect_ratio'],
                resolution=args.resolution
            )

            # Poll for completion
            result_urls = poll_task_status(task_id, config['kie_api_key'])

            # Update Airtable with the first result URL
            if result_urls:
                update_airtable_with_image(
                    config['airtable_token'],
                    config['airtable_base_id'],
                    record_id,
                    result_urls[0],
                    field_name='start_image'
                )
                successful += 1
            else:
                print("⚠️  No result URLs returned")
                failed += 1

        except Exception as e:
            print(f"❌ Error processing scene: {e}")
            failed += 1

        # Small delay between scenes to avoid rate limits
        if i < len(scenes):
            time.sleep(2)

    # Summary
    print(f"\n{'=' * 80}")
    print("📊 GENERATION SUMMARY")
    print(f"{'=' * 80}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"💰 Actual cost: ${successful * model_config['cost']:.4f}")
    print(f"{'=' * 80}")

    if successful > 0:
        print(f"\n✨ Done! Check your Airtable base to see the generated images.")
        print(f"   Base URL: https://airtable.com/{config['airtable_base_id']}")


if __name__ == '__main__':
    main()
