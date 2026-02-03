"""
Setup checker for local inference_pipeline development.

Verifies that Qdrant is accessible, has vectors, and OpenAI is configured.
"""

import sys
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

def check_qdrant():
    """Check if Qdrant is accessible and has vectors."""
    print("\n✓ Checking Qdrant connection...")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host='localhost', port=6333, timeout=5)
        
        # Get collections
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        print(f"  ✅ Qdrant connected")
        print(f"     Host: localhost:6333")
        print(f"     Collections: {collection_names if collection_names else 'none'}")
        
        if not collection_names:
            print(f"  ⚠️  No collections found. Run feature_pipeline to create vectors.")
            return False
        
        # Check for vector collection
        has_vectors = False
        for name in collection_names:
            info = client.get_collection(name)
            print(f"       - {name}: {info.points_count} vectors")
            if info.points_count > 0:
                has_vectors = True
        
        if not has_vectors:
            print(f"  ⚠️  No vectors found. Run feature_pipeline to populate Qdrant.")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Qdrant connection failed: {str(e)}")
        print(f"\n  Make sure Qdrant is running:")
        print(f"    docker-compose up qdrant -d")
        return False

def check_openai():
    """Check if OpenAI API is configured."""
    print("\n✓ Checking OpenAI configuration...")
    
    try:
        from config import settings
        
        if not settings.OPENAI_API_KEY:
            print(f"  ❌ OPENAI_API_KEY not set")
            print(f"\n  Add to .env file:")
            print(f"    OPENAI_API_KEY=your-key-here")
            return False
        
        # Test API call
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL_ID,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        
        print(f"  ✅ OpenAI API working")
        print(f"     Model: {settings.OPENAI_MODEL_ID}")
        print(f"     API Key: {settings.OPENAI_API_KEY[:10]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ OpenAI API check failed: {str(e)}")
        print(f"\n  Possible issues:")
        print(f"    - Invalid API key")
        print(f"    - No credits/quota")
        print(f"    - Network connectivity")
        return False

def check_embedding_model():
    """Check if embedding model can be loaded."""
    print("\n✓ Checking embedding model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print(f"  Loading model: BAAI/bge-small-en-v1.5...")
        model = SentenceTransformer('BAAI/bge-small-en-v1.5')
        
        print(f"  ✅ Embedding model loaded")
        print(f"     Model: BAAI/bge-small-en-v1.5")
        print(f"     Device: {model.device}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Embedding model loading failed: {str(e)}")
        return False

def check_gradio():
    """Check if Gradio is installed."""
    print("\n✓ Checking Gradio...")
    
    try:
        import gradio as gr
        print(f"  ✅ Gradio installed")
        print(f"     Version: {gr.__version__}")
        return True
    except ImportError:
        print(f"  ❌ Gradio not installed")
        print(f"\n  Install with:")
        print(f"    poetry add gradio")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    print("\n✓ Checking Python dependencies...")
    
    required = {
        "sentence_transformers": "Embedding model",
        "qdrant_client": "Vector database client",
        "openai": "OpenAI API client",
        "gradio": "Web UI framework",
        "opik": "Monitoring (optional)",
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✅ {package} ({description})")
        except ImportError:
            if package == "opik":
                print(f"  ⚠️  {package} - OPTIONAL")
            else:
                print(f"  ❌ {package} - NOT INSTALLED")
                missing.append(package)
    
    if missing:
        print(f"\n  Install with:")
        print(f"    poetry install")
        return False
    
    return True

def main():
    print("="*80)
    print("🔍 Inference Pipeline - Setup Checker")
    print("="*80)
    
    checks = [
        ("Python Dependencies", check_dependencies),
        ("Qdrant & Vectors", check_qdrant),
        ("OpenAI API", check_openai),
        ("Embedding Model", check_embedding_model),
        ("Gradio UI", check_gradio),
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
        print("\n🎉 All checks passed! You can run inference_pipeline:")
        print("\n   CLI mode:")
        print("   cd src\\inference_pipeline")
        print("   poetry run python run_local.py")
        print("\n   Web UI mode:")
        print("   poetry run python run_local_ui.py")
        print("   Then open: http://localhost:7860")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nQuick setup:")
        print("   1. poetry install")
        print("   2. docker-compose up qdrant -d")
        print("   3. Run feature_pipeline to create vectors")
        print("   4. Add OPENAI_API_KEY to .env")
    
    print("="*80)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
