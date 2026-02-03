"""
Setup checker for local data_cdc development.

Verifies that MongoDB and RabbitMQ are accessible.
"""

import sys
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

def check_mongodb():
    """Check if MongoDB is accessible."""
    print("\n✓ Checking MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        
        client = MongoClient(
            "mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set",
            serverSelectionTimeoutMS=5000
        )
        
        info = client.server_info()
        print(f"  ✅ MongoDB connected")
        print(f"     Version: {info['version']}")
        
        # Check database and collections
        db = client['twin']
        collections = db.list_collection_names()
        print(f"     Database: twin")
        print(f"     Collections: {collections if collections else 'none (empty)'}")
        
        # Check if there's data to watch
        total_docs = sum(db[coll].count_documents({}) for coll in collections if coll in ['articles', 'posts', 'repositories'])
        print(f"     Documents to watch: {total_docs}")
        
        if total_docs == 0:
            print(f"  ⚠️  No documents found. Run data_crawling first to create data.")
        
        return True
        
    except Exception as e:
        print(f"  ❌ MongoDB connection failed: {str(e)}")
        print(f"\n  Make sure MongoDB is running:")
        print(f"    docker-compose up mongo1 mongo2 mongo3 -d")
        return False

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
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"  ❌ RabbitMQ connection failed: {str(e)}")
        print(f"\n  Make sure RabbitMQ is running:")
        print(f"    docker-compose up mq -d")
        print(f"\n  Check port mapping in docker-compose.yml:")
        print(f"    ports: \"5673:5672\" (host:container)")
        return False

def main():
    print("="*80)
    print("🔍 Data CDC - Setup Checker")
    print("="*80)
    
    checks = [
        ("MongoDB", check_mongodb),
        ("RabbitMQ", check_rabbitmq),
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
        print("\n🎉 All checks passed! You can run data_cdc:")
        print("\n   cd src\\data_cdc")
        print("   poetry run python run_local.py")
        print("\n   Then insert data using data_crawling to see CDC in action!")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick setup:")
        print("   docker-compose up mongo1 mongo2 mongo3 mq -d")
    
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
