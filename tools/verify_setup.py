#!/usr/bin/env python3
"""
Setup Verification Script for Creative Cloner

Checks that all prerequisites are installed and configured.
"""

import sys
import os
import subprocess
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def check_python_version():
    """Check Python version is 3.8+"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg...")
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   ✅ {version}")
            return True
        else:
            print("   ❌ FFmpeg found but returned error")
            return False
    except FileNotFoundError:
        print("   ❌ FFmpeg not installed")
        print("      Install: https://ffmpeg.org/download.html")
        return False
    except Exception as e:
        print(f"   ❌ Error checking FFmpeg: {e}")
        return False

def check_dependencies():
    """Check if Python packages are installed"""
    print("\n📦 Checking Python dependencies...")
    required = [
        'google.genai',
        'dotenv',
        'yaml',
        'pyairtable',
        'requests'
    ]

    all_installed = True
    for package in required:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} not installed")
            all_installed = False

    if not all_installed:
        print("\n   Run: pip install -r requirements.txt")

    return all_installed

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\n🔑 Checking environment configuration...")

    env_path = Path(__file__).parent.parent / '.agent' / '.env'

    if not env_path.exists():
        print(f"   ❌ .env file not found")
        print(f"      Expected: {env_path}")
        print("      Run: cp .env.example .agent/.env")
        return False

    print(f"   ✅ .env file exists")

    # Check for required keys
    required_keys = [
        'GEMINI_API_KEY',
        'KIE_API_KEY',
        'AIRTABLE_API_TOKEN',
        'AIRTABLE_BASE_ID'
    ]

    missing_keys = []
    with open(env_path, 'r') as f:
        content = f.read()
        for key in required_keys:
            if f"{key}=" not in content or f"{key}=your_" in content:
                missing_keys.append(key)

    if missing_keys:
        print("   ⚠️  Missing or placeholder API keys:")
        for key in missing_keys:
            print(f"      - {key}")
        return False
    else:
        print("   ✅ All API keys configured")
        return True

def check_directories():
    """Check if required directories exist"""
    print("\n📁 Checking directories...")

    base_path = Path(__file__).parent.parent
    required_dirs = ['inputs', 'outputs', 'tools']

    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_path / dir_name
        if dir_path.exists():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ⚠️  {dir_name}/ not found (will be created when needed)")

    return True

def main():
    print("=" * 80)
    print("🔍 Creative Cloner - Setup Verification")
    print("=" * 80)

    checks = [
        ("Python Version", check_python_version()),
        ("FFmpeg", check_ffmpeg()),
        ("Python Dependencies", check_dependencies()),
        ("Environment File", check_env_file()),
        ("Directories", check_directories())
    ]

    print("\n" + "=" * 80)
    print("📊 Summary")
    print("=" * 80)

    all_passed = True
    for name, passed in checks:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 80)

    if all_passed:
        print("\n🎉 All checks passed! You're ready to use Creative Cloner.")
        print("\nNext steps:")
        print("  1. Place a video in inputs/ folder")
        print("  2. Run: python tools/analyze_video.py")
        print("  3. Follow the workflow in README.md")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
