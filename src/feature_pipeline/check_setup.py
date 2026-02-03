"""
Setup checker for local feature_pipeline development.

Verifies that RabbitMQ and Qdrant are accessible, and embedding model can be loaded.
"""

import sys
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

def check_rabbitmq():
    """Check if RabbitMQ is accessible."""
    print("\n✓ Checking RabbitMQ connection...")
    
    try:
        import pika
        
        credentials = pika.PlainCredentials('guest', 'guest')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5673,
                credentials=credentials
            )
        )
        
        channel = connection.channel()
        channel.queue_declare(queue='default', durable=True)
        
        # Get queue info
        method = channel.queue_declare(queue='default', passive=True)
        message_count = method.method.message_count
        
        print(f"  ✅ RabbitMQ connected")
        print(f"     Host: localhost:5673")
        print(f"     Queue: default")
        print(f"     Messages in queue: {message_count}")
        
        if message_count == 0:
            print(f"  ⚠️  No messages in queue. Run data_cdc to populate messages.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"  ❌ RabbitMQ connection failed: {str(e)}")
        print(f"\n  Make sure RabbitMQ is running:")
        print(f"    docker-compose up mq -d")
        return False

def check_qdrant():
    """Check if Qdrant is accessible."""
    print("\n✓ Checking Qdrant connection...")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host='localhost', port=6333, timeout=5)
        
        # Get collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        print(f"  ✅ Qdrant connected")
        print(f"     Host: localhost:6333")
        print(f"     Collections: {collection_names if collection_names else 'none (empty)'}")
        
        # Check collection sizes
        for name in collection_names:
            info = client.get_collection(name)
            print(f"       - {name}: {info.points_count} vectors")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Qdrant connection failed: {str(e)}")
        print(f"\n  Make sure Qdrant is running:")
        print(f"    docker-compose up qdrant -d")
        return False

def check_embedding_model():
    """Check if embedding model can be loaded."""
    print("\n✓ Checking embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print(f"  Loading model: BAAI/bge-small-en-v1.5...")
        model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        
        # Test encoding
        test_embedding = model.encode(["test"], show_progress_bar=False)
        
        print(f"  ✅ Embedding model loaded")
        print(f"     Model: BAAI/bge-small-en-v1.5")
        print(f"     Embedding size: {len(test_embedding[0])}")
        print(f"     Device: {model.device}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Embedding model loading failed: {str(e)}")
        print(f"\n  The model will be downloaded on first use.")
        print(f"  Make sure you have internet connection and enough disk space.")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\n✓ Checking Python dependencies...")
    
    required = {
        "bytewax": "Streaming framework",
        "sentence_transformers": "Embedding model",
        "qdrant_client": "Vector database client",
        "pika": "RabbitMQ client",
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✅ {package} ({description})")
        except ImportError:
            print(f"  ❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    if missing:
        print(f"\n  Install with:")
        print(f"    poetry install")
        return False
    
    return True

def main():
    print("="*80)
    print("🔍 Feature Pipeline - Setup Checker")
    print("="*80)
    
    checks = [
        ("Python Dependencies", check_dependencies),
        ("RabbitMQ", check_rabbitmq),
        ("Qdrant", check_qdrant),
        ("Embedding Model", check_embedding_model),
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
        print("\n🎉 All checks passed! You can run feature_pipeline:")
        print("\n   cd src\\feature_pipeline")
        print("   poetry run python run_local.py")
        print("\n   Make sure data_cdc is running to populate messages!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick setup:")
        print("   1. poetry install")
        print("   2. docker-compose up mq qdrant -d")
    
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
