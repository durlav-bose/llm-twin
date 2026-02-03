"""
Local runner for data_cdc (Change Data Capture) without Docker.

This script watches MongoDB for changes and publishes them to RabbitMQ.
Both MongoDB and RabbitMQ should be running in Docker.

Architecture:
    MongoDB (Docker) → data_cdc (Local) → RabbitMQ (Docker)

Usage:
    python run_local.py
"""

import sys
from pathlib import Path

# Add src to path for imports
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

from config import settings
from cdc import stream_process
import core.config as core_config

# Patch settings to use localhost
settings.patch_localhost()
core_config.settings.patch_localhost()

print("="*80)
print("🚀 LLM Twin - Data CDC (Change Data Capture)")
print("="*80)
print(f"✓ MongoDB: {settings.MONGO_DATABASE_HOST}")
print(f"✓ Database: {settings.MONGO_DATABASE_NAME}")
print(f"✓ RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
print(f"✓ Queue: {settings.RABBITMQ_QUEUE_NAME}")
print("="*80)
print("\n📡 Watching MongoDB for changes...")
print("   Supported collections: articles, posts, repositories")
print("   Press Ctrl+C to stop\n")
print("="*80)

if __name__ == "__main__":
    try:
        stream_process()
    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("⏹️  Stopped by user")
        print("="*80)
    except Exception as e:
        print("\n\n" + "="*80)
        print(f"❌ Error: {str(e)}")
        print("="*80)
        import traceback
        traceback.print_exc()
