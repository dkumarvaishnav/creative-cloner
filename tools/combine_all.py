#!/usr/bin/env python3
"""
Video Combiner for Creative Cloner

Combines multiple video clips into one final video using FFmpeg.
Optionally adds background music with fade-out.
"""

import os
import sys
import argparse
import subprocess
import re
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def check_ffmpeg_installed():
    """Check if FFmpeg is installed and accessible"""
    print("🔍 Checking for FFmpeg...")
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            print(f"✅ FFmpeg found: {version_line}")
            return True
        else:
            print("❌ FFmpeg found but returned an error")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg not found!")
        print("\n   Please install FFmpeg:")
        print("   - Windows: Download from https://ffmpeg.org/download.html")
        print("   - Mac: brew install ffmpeg")
        print("   - Linux: sudo apt-get install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ Error checking FFmpeg: {e}")
        return False


def find_video_files(input_dir, project_name=None):
    """Find all video files in directory, optionally filtered by project name"""
    print(f"\n📂 Looking for videos in: {input_dir}")

    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Directory not found: {input_dir}")
        return []

    # Find all .mp4 files
    video_files = list(input_path.glob('*.mp4'))

    if project_name:
        # Filter by project name in filename
        video_files = [f for f in video_files if project_name.lower() in f.name.lower()]

    if not video_files:
        print(f"❌ No video files found")
        if project_name:
            print(f"   (filtered by project name: {project_name})")
        return []

    # Sort by scene number (extract number from filename)
    def get_scene_number(filename):
        # Try to extract scene number from filename like "scene_1_..."
        match = re.search(r'scene[_\s]*(\d+)', filename.name, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # If no scene number found, use filename alphabetically
        return filename.name

    video_files.sort(key=get_scene_number)

    print(f"✅ Found {len(video_files)} video(s):")
    for i, video in enumerate(video_files, 1):
        size_mb = video.stat().st_size / (1024 * 1024)
        print(f"   {i}. {video.name} ({size_mb:.2f} MB)")

    return video_files


def create_concat_file(video_files, concat_file_path):
    """Create FFmpeg concat file listing all videos"""
    print(f"\n📝 Creating concat file: {concat_file_path.name}")

    with open(concat_file_path, 'w', encoding='utf-8') as f:
        for video in video_files:
            # Use absolute path and escape special characters
            abs_path = video.resolve()
            # FFmpeg concat format: file 'path'
            # Use forward slashes even on Windows (FFmpeg prefers this)
            path_str = str(abs_path).replace('\\', '/')
            f.write(f"file '{path_str}'\n")

    print(f"✅ Concat file created with {len(video_files)} video(s)")


def combine_videos(concat_file, output_file, copy_codec=True):
    """Combine videos using FFmpeg"""
    print(f"\n🎬 Combining videos...")
    print(f"   Output: {output_file}")

    if copy_codec:
        # Use -c copy for fast concatenation (no re-encoding)
        print(f"   Mode: Fast (copy codec, no re-encoding)")
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            '-y',  # Overwrite output file
            str(output_file)
        ]
    else:
        # Re-encode (slower but more compatible)
        print(f"   Mode: Re-encode (slower, more compatible)")
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-y',
            str(output_file)
        ]

    try:
        # Run FFmpeg with progress output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )

        if result.returncode == 0:
            output_path = Path(output_file)
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"✅ Videos combined successfully! ({size_mb:.2f} MB)")
                return True
            else:
                print(f"❌ FFmpeg succeeded but output file not found")
                return False
        else:
            print(f"❌ FFmpeg failed:")
            print(f"   Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timed out (took more than 5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Error running FFmpeg: {e}")
        return False


def add_background_music(video_file, music_file, output_file, fade_duration=2):
    """Add background music to video with fade-out"""
    print(f"\n🎵 Adding background music...")
    print(f"   Music: {music_file}")
    print(f"   Fade-out: {fade_duration}s")

    music_path = Path(music_file)
    if not music_path.exists():
        print(f"❌ Music file not found: {music_file}")
        return False

    # FFmpeg command to add music with fade-out
    # Calculate fade start time (we'll use -shortest, so fade starts at video duration - fade_duration)
    cmd = [
        'ffmpeg',
        '-i', str(video_file),
        '-i', str(music_file),
        '-filter_complex',
        f'[1:a]afade=t=out:st=0:d={fade_duration}[audio]',
        '-map', '0:v',  # Video from first input
        '-map', '[audio]',  # Faded audio
        '-c:v', 'copy',  # Copy video codec (no re-encoding)
        '-c:a', 'aac',  # Encode audio as AAC
        '-shortest',  # Stop when shortest stream ends (video)
        '-y',
        str(output_file)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            output_path = Path(output_file)
            if output_path.exists():
                size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"✅ Music added successfully! ({size_mb:.2f} MB)")
                return True
            else:
                print(f"❌ FFmpeg succeeded but output file not found")
                return False
        else:
            print(f"❌ FFmpeg failed:")
            print(f"   Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ FFmpeg timed out")
        return False
    except Exception as e:
        print(f"❌ Error adding music: {e}")
        return False


def cleanup_temp_files(files):
    """Clean up temporary files"""
    print(f"\n🗑️  Cleaning up temporary files...")

    cleaned = 0
    for file in files:
        try:
            file_path = Path(file)
            if file_path.exists():
                file_path.unlink()
                print(f"   ✓ Deleted: {file_path.name}")
                cleaned += 1
        except Exception as e:
            print(f"   ⚠️  Could not delete {file}: {e}")

    if cleaned > 0:
        print(f"✅ Cleaned up {cleaned} temporary file(s)")


def main():
    parser = argparse.ArgumentParser(
        description='Combine multiple video clips into one final video using FFmpeg',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Combine all videos in outputs/
  python tools/combine_all.py

  # Combine videos for a specific project
  python tools/combine_all.py --project-name "My Project"

  # Add background music
  python tools/combine_all.py --music inputs/background.mp3

  # Preview without combining
  python tools/combine_all.py --dry-run

  # Custom output location
  python tools/combine_all.py --output final_videos/my_video.mp4
        '''
    )
    parser.add_argument(
        '--input-dir',
        default='outputs',
        help='Directory containing video files (default: outputs/)'
    )
    parser.add_argument(
        '--output',
        default='outputs/final_video.mp4',
        help='Output filename (default: outputs/final_video.mp4)'
    )
    parser.add_argument(
        '--project-name',
        help='Filter videos by project name (optional)'
    )
    parser.add_argument(
        '--music',
        help='Background music file to add (optional)'
    )
    parser.add_argument(
        '--fade-duration',
        type=int,
        default=2,
        help='Fade-out duration for music in seconds (default: 2)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview what would be done without actually combining'
    )
    parser.add_argument(
        '--re-encode',
        action='store_true',
        help='Re-encode videos (slower but more compatible, use if fast mode fails)'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🎬 Creative Cloner - Video Combiner")
    print("=" * 80)

    # Check FFmpeg
    if not check_ffmpeg_installed():
        sys.exit(1)

    # Find video files
    video_files = find_video_files(args.input_dir, args.project_name)
    if not video_files:
        sys.exit(1)

    if len(video_files) == 1:
        print("\n⚠️  Only one video found. Nothing to combine.")
        print(f"   Video: {video_files[0]}")
        sys.exit(0)

    # Dry-run mode
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No files will be created")
        print("\nWould combine these videos in order:")
        for i, video in enumerate(video_files, 1):
            size_mb = video.stat().st_size / (1024 * 1024)
            print(f"   {i}. {video.name} ({size_mb:.2f} MB)")
        print(f"\nOutput would be: {args.output}")
        if args.music:
            print(f"Background music would be: {args.music}")
            print(f"Music fade-out: {args.fade_duration}s")
        print("\n✅ Dry run complete")
        return

    # Create temporary concat file
    concat_file = Path(args.input_dir) / 'videos_concat_list.txt'
    temp_files = [concat_file]

    try:
        # Create concat file
        create_concat_file(video_files, concat_file)

        # Determine output files
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.music:
            # If music is provided, combine to temp file first, then add music
            temp_output = output_path.parent / f"temp_{output_path.name}"
            temp_files.append(temp_output)

            # Combine videos
            success = combine_videos(
                concat_file,
                temp_output,
                copy_codec=not args.re_encode
            )

            if not success:
                print("\n⚠️  If the error mentions 'Non-monotonous DTS', try using --re-encode flag")
                cleanup_temp_files(temp_files)
                sys.exit(1)

            # Add music
            success = add_background_music(
                temp_output,
                args.music,
                output_path,
                args.fade_duration
            )

            if not success:
                cleanup_temp_files(temp_files)
                sys.exit(1)
        else:
            # No music, just combine
            success = combine_videos(
                concat_file,
                output_path,
                copy_codec=not args.re_encode
            )

            if not success:
                print("\n⚠️  If the error mentions 'Non-monotonous DTS', try using --re-encode flag")
                cleanup_temp_files(temp_files)
                sys.exit(1)

        # Clean up temp files
        cleanup_temp_files(temp_files)

        # Success summary
        print("\n" + "=" * 80)
        print("✅ VIDEO COMBINATION COMPLETE!")
        print("=" * 80)
        print(f"📹 Final video: {output_path.resolve()}")
        print(f"📊 Combined {len(video_files)} video(s)")
        if args.music:
            print(f"🎵 Background music: {args.music}")

        # Show file size
        final_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"💾 File size: {final_size_mb:.2f} MB")
        print("=" * 80)

        print("\n✨ Done! Your final video is ready.")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        cleanup_temp_files(temp_files)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        cleanup_temp_files(temp_files)
        sys.exit(1)


if __name__ == '__main__':
    main()
