"""
Local runner for data crawling without Docker/Lambda.

This script allows you to run the data crawler locally for testing and development.
MongoDB should still be running in Docker.

Usage:
    python run_local.py
"""

import sys
from pathlib import Path

# Add src to path for imports
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

from config import settings
from main import handler

# Patch settings to use localhost for MongoDB
settings.patch_localhost()
print(f"✓ Patched MongoDB connection to: {settings.MONGO_DATABASE_HOST}")

if __name__ == "__main__":
    # Example: Medium article
    print("\n" + "="*80)
    print("Testing Medium Article Crawler")
    print("="*80)
    
    event = {
        "user": "Paul Iusztin",
        "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f"
    }
    
    print(f"\nCrawling: {event['link']}")
    print(f"User: {event['user']}\n")
    
    result = handler(event, None)
    print(f"\nResult: {result}")
    
    # Example: GitHub repository
    print("\n" + "="*80)
    print("Testing GitHub Repository Crawler")
    print("="*80)
    
    event = {
        "user": "Paul Iusztin",
        "link": "https://github.com/decodingml/llm-twin-course"
    }
    
    print(f"\nCrawling: {event['link']}")
    print(f"User: {event['user']}\n")
    
    result = handler(event, None)
    print(f"\nResult: {result}")
    
    print("\n" + "="*80)
    print("✓ Done! Check MongoDB Compass to see the crawled data.")
    print("="*80)
