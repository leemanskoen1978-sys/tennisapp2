#!/usr/bin/env python3
"""
Test script to verify the tennis scraper setup is working.
Run from Webscraping/ folder.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("🔍 Testing tennis scraper setup...")

try:
    print("📦 Testing Python packages...")
    import playwright
    print("✅ playwright imported successfully")
    
    from tennis_lessen_scraper.main import cmd_scrape
    print("✅ Main module imported successfully")
    
    from tennis_lessen_scraper.calendar_scraper import get_private_lessons
    print("✅ Google Calendar module imported successfully")
    
    print("🎯 All imports working!")
    print("\n✨ Ready to run: python run_tennis_scraper.py --setup")
    print("✨ Or directly: python run_tennis_scraper.py --scrape")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try running: pip install -r tennis_lessen_scraper/requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)