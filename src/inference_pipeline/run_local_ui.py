"""
Local runner for inference_pipeline - Gradio UI version.

This script launches a web UI for chatting with your LLM Twin.

Usage:
    python run_local_ui.py
    
Then open: http://localhost:7860
"""

import sys
from pathlib import Path

# Add src to path for imports
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

from config import settings
import core.config as core_config
from llm_twin import LLMTwin
import gradio as gr

# Patch settings to use localhost
settings.patch_localhost()
core_config.settings.patch_localhost()

print("="*80)
print("🚀 LLM Twin - Inference Pipeline (Gradio UI)")
print("="*80)
print(f"✓ Qdrant: {settings.QDRANT_DATABASE_HOST}:{settings.QDRANT_DATABASE_PORT}")
print(f"✓ Embedding Model: {settings.EMBEDDING_MODEL_ID}")
print(f"✓ LLM: {settings.OPENAI_MODEL_ID if settings.USE_LOCAL_LLM else settings.MODEL_ID}")
print(f"✓ Mode: {'Local (OpenAI)' if settings.USE_LOCAL_LLM else 'SageMaker'}")
print("="*80)
print("\n⏳ Initializing LLM Twin...")

# Initialize LLM Twin
llm_twin = LLMTwin(mock=False)

print("✅ LLM Twin initialized!")
print("\n🌐 Starting Gradio UI...")
print("   Access at: http://localhost:7860")
print("   Press Ctrl+C to stop\n")
print("="*80)


def predict(message: str, history: list[list[str]], author: str) -> str:
    """
    Generates a response using the LLM Twin.

    Args:
        message: The user's input message or question.
        history: Previous conversation history.
        author: The author's name for personalization.

    Returns:
        The LLM Twin's generated response.
    """
    query = f"I am {author}. Write about: {message}"
    
    try:
        response = llm_twin.generate(
            query=query, 
            enable_rag=True, 
            sample_for_evaluation=False
        )
        return response["answer"]
    except Exception as e:
        return f"Error generating response: {str(e)}\n\nPlease check:\n- Qdrant is running (docker ps | grep qdrant)\n- You have vectors in Qdrant\n- OpenAI API key is valid"


demo = gr.ChatInterface(
    predict,
    textbox=gr.Textbox(
        placeholder="Chat with your LLM Twin",
        label="Message",
        container=False,
        scale=7,
    ),
    additional_inputs=[
        gr.Textbox(
            "Paul Iusztin",
            label="Who are you?",
        )
    ],
    title="Your LLM Twin 🤖",
    description="""
    Chat with your personalized LLM Twin! This AI assistant will help you write content incorporating your style and voice.
    
    **How it works:**
    1. Your message is sent to the RAG system
    2. Relevant context is retrieved from Qdrant
    3. LLM generates a response in your style
    
    **Requirements:**
    - Qdrant running with embedded vectors
    - OpenAI API key configured
    """,
    theme="soft",
    examples=[
        [
            "Draft a post about RAG systems.",
            "Paul Iusztin",
        ],
        [
            "Draft an article paragraph about vector databases.",
            "Paul Iusztin",
        ],
        [
            "Draft a post about LLM chatbots and their applications.",
            "Paul Iusztin",
        ],
        [
            "Write about machine learning deployment best practices.",
            "Paul Iusztin",
        ],
    ],
    cache_examples=False,
)


if __name__ == "__main__":
    try:
        demo.queue().launch(
            server_name="127.0.0.1",  # Localhost only
            server_port=7860,
            share=False,  # Don't create public link
            show_error=True
        )
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
