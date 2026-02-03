"""
Setup checker for local data crawler development.

This script verifies that all prerequisites are installed and configured correctly.
"""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python 3.11 is being used."""
    version = sys.version_info
    print(f"\n✓ Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 11:
        print("  ✅ Correct Python version (3.11)")
        return True
    else:
        print(f"  ❌ Wrong Python version. Project requires Python 3.11")
        print(f"\n  Fix with:")
        print(f"    poetry env use python3.11")
        print(f"    poetry install")
        return False

def check_chrome():
    """Check if Chrome is installed."""
    print(f"\n✓ Checking Chrome installation...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "/usr/bin/google-chrome",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    ]
    
    for path in chrome_paths:
        if Path(path).exists():
            print(f"  ✅ Chrome found at: {path}")
            return True
    
    print(f"  ⚠️  Chrome not found in standard locations")
    print(f"  Install from: https://www.google.com/chrome/")
    return False

def check_mongodb():
    """Check if MongoDB containers are running."""
    print(f"\n✓ Checking MongoDB containers...")
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=mongo", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            check=True
        )
        
        containers = result.stdout.strip().split('\n')
        containers = [c for c in containers if c]  # Remove empty strings
        
        if len(containers) >= 3:
            print(f"  ✅ MongoDB containers running:")
            for container in containers:
                print(f"     - {container}")
            return True
        else:
            print(f"  ❌ MongoDB containers not running")
            print(f"\n  Start with:")
            print(f"    docker-compose up mongo1 mongo2 mongo3 -d")
            return False
            
    except subprocess.CalledProcessError:
        print(f"  ❌ Docker not running or not installed")
        return False
    except FileNotFoundError:
        print(f"  ❌ Docker command not found")
        return False

def check_dependencies():
    """Check if required Python packages are installed."""
    print(f"\n✓ Checking Python dependencies...")
    
    required_packages = [
        "pydantic",
        "pydantic_settings",
        "selenium",
        "pymongo",
        "langchain_community"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n  Install with:")
        print(f"    poetry install")
        return False
    
    return True

def check_mongodb_connection():
    """Try to connect to MongoDB."""
    print(f"\n✓ Testing MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient(
            "mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set",
            serverSelectionTimeoutMS=5000
        )
        
        # Try to get server info
        info = client.server_info()
        print(f"  ✅ MongoDB connection successful")
        print(f"     Version: {info['version']}")
        
        # Check database
        db = client['twin']
        collections = db.list_collection_names()
        print(f"     Database: twin")
        print(f"     Collections: {collections if collections else 'none (empty database)'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB connection failed: {str(e)}")
        print(f"\n  Make sure MongoDB is running:")
        print(f"    docker-compose up mongo1 mongo2 mongo3 -d")
        return False

def main():
    print("="*80)
    print("🔍 LLM Twin - Data Crawler Setup Checker")
    print("="*80)
    
    checks = [
        ("Python 3.11", check_python_version),
        ("Chrome Browser", check_chrome),
        ("MongoDB Containers", check_mongodb),
        ("Python Dependencies", check_dependencies),
        ("MongoDB Connection", check_mongodb_connection),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append((name, check_func()))
        except Exception as e:
            print(f"  ❌ Error checking {name}: {str(e)}")
            results.append((name, False))
    
    print("\n" + "="*80)
    print("📊 Summary")
    print("="*80)
    
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    print("="*80)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run the crawler:")
        print("\n   cd src\\data_crawling")
        print("   poetry run python run_local_enhanced.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick setup commands:")
        print("   1. poetry env use python3.11")
        print("   2. poetry install")
        print("   3. docker-compose up mongo1 mongo2 mongo3 -d")
    
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
