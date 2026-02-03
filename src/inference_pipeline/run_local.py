"""
Local runner for inference_pipeline - Simple CLI version.

This script allows you to test the RAG-powered LLM Twin locally using OpenAI.

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
from llm_twin import LLMTwin

# Patch settings to use localhost
settings.patch_localhost()
core_config.settings.patch_localhost()

print("="*80)
print("🚀 LLM Twin - Inference Pipeline (CLI)")
print("="*80)
print(f"✓ Qdrant: {settings.QDRANT_DATABASE_HOST}:{settings.QDRANT_DATABASE_PORT}")
print(f"✓ Embedding Model: {settings.EMBEDDING_MODEL_ID}")
print(f"✓ LLM: {settings.OPENAI_MODEL_ID if settings.USE_LOCAL_LLM else settings.MODEL_ID}")
print(f"✓ Mode: {'Local (OpenAI)' if settings.USE_LOCAL_LLM else 'SageMaker'}")
print(f"✓ RAG Config:")
print(f"   - Top K: {settings.TOP_K}")
print(f"   - Keep Top K: {settings.KEEP_TOP_K}")
print(f"   - Expand N Queries: {settings.EXPAND_N_QUERY}")
print("="*80)

if __name__ == "__main__":
    # Initialize LLM Twin
    print("\n⏳ Initializing LLM Twin...")
    llm_twin = LLMTwin(mock=False)
    print("✅ LLM Twin initialized!\n")
    
    # Example queries
    test_queries = [
        {
            "author": "Paul Iusztin",
            "query": "Draft an article paragraph about RAG systems and how to design them effectively."
        },
        {
            "author": "Paul Iusztin", 
            "query": "Write a post about vector databases and their role in AI applications."
        },
    ]
    
    for i, test in enumerate(test_queries, 1):
        print("="*80)
        print(f"Test Query {i}/{len(test_queries)}")
        print("="*80)
        print(f"Author: {test['author']}")
        print(f"Query: {test['query']}")
        print("-"*80)
        
        # Format query
        full_query = f"I am {test['author']}. Write about: {test['query']}"
        
        print("\n⏳ Generating response...")
        response = llm_twin.generate(
            query=full_query,
            enable_rag=True,
            sample_for_evaluation=False
        )
        
        print("\n📝 Response:")
        print("-"*80)
        print(response['answer'])
        print("-"*80)
        
        if response.get('context'):
            print(f"\n📚 Retrieved {len(response['context'])} context documents")
            print("-"*80)
            for j, ctx in enumerate(response['context'][:3], 1):
                print(f"\nContext {j}:")
                print(f"  Score: {ctx.get('score', 'N/A')}")
                print(f"  Content: {str(ctx)[:200]}...")
        
        print("\n")
    
    print("="*80)
    print("✅ All queries completed!")
    print("\nℹ️  To test interactively, run: python run_local_ui.py")
    print("="*80)
