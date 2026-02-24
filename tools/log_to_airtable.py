#!/usr/bin/env python3
"""
Airtable Logger for Creative Cloner

Logs scene prompts to Airtable for tracking the creative cloning workflow.

Table Structure:
- Project Name: Single line text
- scene: Single line text (e.g., "Scene 1 - Title")
- start_image_prompt: Long text
- video_prompt: Long text
- start_image: Attachment (for generated images)
- scene_video: Attachment (for generated videos)
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv
import yaml
from pyairtable import Api

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def load_config():
    """Load Airtable API key and Base ID from .env file"""
    env_path = Path(__file__).parent.parent / '.agent' / '.env'
    load_dotenv(env_path)

    # Try both AIRTABLE_API_TOKEN and AIRTABLE_API_KEY for compatibility
    api_key = os.getenv('AIRTABLE_API_TOKEN') or os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')

    if not api_key:
        print("❌ Error: AIRTABLE_API_TOKEN/AIRTABLE_API_KEY not found in .agent/.env file")
        print(f"   Please add your API key to: {env_path}")
        print("   Format: AIRTABLE_API_TOKEN=your_key_here")
        sys.exit(1)

    if not base_id:
        print("❌ Error: AIRTABLE_BASE_ID not found in .agent/.env file")
        print(f"   Please add your Base ID to: {env_path}")
        print("   Format: AIRTABLE_BASE_ID=your_base_id")
        sys.exit(1)

    return api_key, base_id


def load_prompts(prompts_path):
    """Load prompts from YAML file"""
    print(f"📖 Loading prompts from: {prompts_path}")

    if not os.path.exists(prompts_path):
        print(f"❌ Error: Prompts file not found: {prompts_path}")
        sys.exit(1)

    with open(prompts_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    prompts = data.get('prompts', [])
    print(f"✅ Loaded {len(prompts)} scene prompts")
    return prompts, data.get('metadata', {})


def create_or_get_table(api, base_id, table_name='Scenes'):
    """Get the table (assumes it exists)"""
    print(f"\n📊 Connecting to Airtable table: {table_name}")
    table = api.table(base_id, table_name)
    print(f"✅ Connected to table: {table_name}")
    return table


def clear_existing_records(table, project_name=None):
    """Clear existing records from the table"""
    print("\n🗑️  Checking for existing records...")

    try:
        if project_name:
            # Only delete records with matching project name
            formula = f"{{Project Name}}='{project_name}'"
            records = table.all(formula=formula)
        else:
            # Delete all records
            records = table.all()

        if records:
            print(f"   Found {len(records)} existing record(s)")
            print("   Deleting existing records...")

            record_ids = [record['id'] for record in records]
            # Delete in batches of 10 (Airtable limit)
            for i in range(0, len(record_ids), 10):
                batch = record_ids[i:i+10]
                table.batch_delete(batch)

            print(f"✅ Deleted {len(records)} existing record(s)")
        else:
            print("✅ No existing records found")
    except Exception as e:
        print(f"⚠️  Warning: Could not clear records: {e}")
        print("   Continuing anyway...")


def log_prompts_to_airtable(table, prompts, project_name):
    """Log prompts to Airtable"""
    print(f"\n📝 Logging {len(prompts)} scenes to Airtable...")

    records_created = []

    for prompt in prompts:
        scene_num = prompt['scene_number']
        scene_desc = prompt['scene_description']

        # Create scene identifier
        scene_id = f"Scene {scene_num}"
        if len(scene_desc) > 50:
            scene_title = scene_desc[:47] + "..."
        else:
            scene_title = scene_desc
        scene_full = f"{scene_id} - {scene_title}"

        # Prepare record
        record = {
            'Project Name': project_name,
            'scene': scene_full,
            'start_image_prompt': prompt['image_prompt'],
            'video_prompt': prompt['video_prompt']
            # start_image and scene_video will be uploaded later
        }

        # Create record in Airtable
        try:
            created = table.create(record)
            print(f"   ✓ Logged: {scene_id}")
            records_created.append(created)
        except Exception as e:
            print(f"   ❌ Error logging {scene_id}: {e}")
            # Continue with other records

    print(f"\n✅ Successfully logged {len(records_created)} records to Airtable")
    return records_created


def display_summary(records, metadata):
    """Display summary of logged records"""
    print("\n" + "=" * 80)
    print("📋 AIRTABLE LOGGING SUMMARY")
    print("=" * 80)
    print(f"Total Scenes: {len(records)}")
    print(f"Total Duration: {metadata.get('total_duration', 'N/A')}")
    print(f"Music/Sound: {metadata.get('music_sound', 'N/A')}")
    print("\nLogged Scenes:")
    for i, record in enumerate(records, 1):
        fields = record['fields']
        print(f"  {i}. {fields['scene']}")
        print(f"     Project: {fields['Project Name']}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Log scene prompts to Airtable for tracking'
    )
    parser.add_argument(
        '-p', '--prompts',
        help='Path to prompts YAML file (default: outputs/prompts.yaml)',
        default='outputs/prompts.yaml'
    )
    parser.add_argument(
        '-n', '--project-name',
        help='Project name for grouping scenes (default: Creative Cloner Project)',
        default='Creative Cloner Project'
    )
    parser.add_argument(
        '-t', '--table',
        help='Airtable table name (default: Scenes)',
        default='Scenes'
    )
    parser.add_argument(
        '--clear',
        help='Clear existing records before logging (default: True)',
        action='store_true',
        default=True
    )

    args = parser.parse_args()

    print("=" * 80)
    print("📊 Creative Cloner - Airtable Logger")
    print("=" * 80)

    # Load Airtable credentials
    api_key, base_id = load_config()
    api = Api(api_key)
    print("✅ Airtable API configured")

    # Load prompts
    prompts, metadata = load_prompts(args.prompts)

    # Connect to table
    table = create_or_get_table(api, base_id, args.table)

    # Clear existing records if requested
    if args.clear:
        clear_existing_records(table, args.project_name)

    # Log prompts
    records = log_prompts_to_airtable(table, prompts, args.project_name)

    # Display summary
    display_summary(records, metadata)

    print("\n✨ Done! Check your Airtable base to see the logged scenes.")
    print(f"   Base URL: https://airtable.com/{base_id}")


if __name__ == '__main__':
    main()
