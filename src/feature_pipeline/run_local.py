"""
Local runner for feature_pipeline without Docker.

This script consumes messages from RabbitMQ, processes them (cleaning, chunking, embedding),
and stores the results in Qdrant vector database.

Architecture:
    RabbitMQ (Docker) → feature_pipeline (Local) → Qdrant (Docker)

Usage:
    python run_local.py
"""

import sys
from pathlib import Path

# Add src to path for imports
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

from config import settings
import core.config as core_config

# Patch settings to use localhost
settings.patch_localhost()
core_config.settings.patch_localhost()

print("="*80)
print("🚀 LLM Twin - Feature Pipeline")
print("="*80)
print(f"✓ RabbitMQ: {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
print(f"✓ Queue: {settings.RABBITMQ_QUEUE_NAME}")
print(f"✓ Qdrant: {settings.QDRANT_DATABASE_HOST}:{settings.QDRANT_DATABASE_PORT}")
print(f"✓ Embedding Model: {settings.EMBEDDING_MODEL_ID}")
print(f"✓ Embedding Size: {settings.EMBEDDING_SIZE}")
print("="*80)
print("\n📊 Processing Pipeline:")
print("   1. Consume from RabbitMQ")
print("   2. Clean data")
print("   3. Chunk into smaller pieces")
print("   4. Generate embeddings")
print("   5. Store in Qdrant")
print("\n   Press Ctrl+C to stop\n")
print("="*80)

if __name__ == "__main__":
    try:
        # Import and run the Bytewax dataflow
        from main import flow
        import bytewax.operators as op
        
        print("\n⏳ Starting Bytewax dataflow...")
        print("   Waiting for messages from RabbitMQ...\n")
        
        # Run the dataflow
        from bytewax.testing import run_main
        run_main(flow)
        
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
