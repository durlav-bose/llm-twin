# Inference Pipeline - Local Development Guide

## Overview

The inference pipeline provides a chat interface where users can interact with their personalized LLM Twin. It combines RAG (Retrieval-Augmented Generation) with LLM to generate responses in your style.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Your Local Machine                                      │
│                                                          │
│  ┌────────────────┐         ┌──────────────┐            │
│  │ Docker         │         │ inference_   │            │
│  │                │         │ pipeline     │            │
│  │ Qdrant         │────────→│ (Python)     │            │
│  │ (6333)         │ RAG     │              │            │
│  └────────────────┘         │ run_local_   │            │
│                             │ ui.py        │            │
│  ┌────────────────┐         └──────┬───────┘            │
│  │ OpenAI API     │                │                    │
│  │ (Cloud)        │←───────────────┘                    │
│  │ gpt-4o-mini    │  LLM generation                     │
│  └────────────────┘                                      │
│                                                          │
│  Browser: http://localhost:7860                         │
└──────────────────────────────────────────────────────────┘
```

## How It Works

### Full Pipeline Flow:

```
User Query
    ↓
1. RAG Retrieval
   ├─ Embed query using BAAI/bge-small-en-v1.5
   ├─ Search Qdrant for similar vectors
   ├─ Retrieve top K=5 relevant chunks
   └─ Rerank and keep top K=5
    ↓
2. Prompt Construction
   ├─ System prompt: "You are writing as [author]"
   ├─ Context: Retrieved relevant chunks
   └─ User query
    ↓
3. LLM Generation
   ├─ LOCAL: OpenAI gpt-4o-mini (for development)
   └─ PRODUCTION: SageMaker fine-tuned model
    ↓
4. Response
   └─ Personalized answer in author's style
```

## Setup

### Prerequisites

```bash
# 1. Qdrant running with vectors
docker-compose up qdrant -d

# 2. Vectors must exist (run feature_pipeline first)
# Terminal 1: Feature Pipeline
cd src\feature_pipeline
poetry run python run_local.py

# Terminal 2: Data CDC  
cd src\data_cdc
poetry run python run_local.py

# Terminal 3: Insert data
cd src\data_crawling
poetry run python run_local_enhanced.py

# 3. OpenAI API key in .env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL_ID=gpt-4o-mini
```

### Check Setup

```bash
cd src\inference_pipeline
poetry run python check_setup.py
```

This verifies:
- ✅ Python dependencies installed
- ✅ Qdrant connection and vectors exist
- ✅ OpenAI API configured and working
- ✅ Embedding model loaded
- ✅ Gradio UI framework installed

## Running Locally

### Option 1: CLI Mode (Testing)

```bash
cd src\inference_pipeline
poetry run python run_local.py
```

Runs test queries and shows:
- Retrieved context
- Generated response
- Token usage

### Option 2: Web UI Mode (Interactive)

```bash
cd src\inference_pipeline
poetry run python run_local_ui.py
```

Then open browser: **http://localhost:7860**

You'll see a chat interface where you can:
- Enter messages
- Specify who you are (author name)
- Get personalized responses
- See real-time generation

## Using the Web UI

### Basic Usage

1. **Enter your name**: "Paul Iusztin" (or your name)
2. **Type a message**: "Draft a post about RAG systems"
3. **Click Submit**
4. **Wait for response** (5-15 seconds)

### Example Queries

```
User: Paul Iusztin
Message: Draft an article paragraph about vector databases.

Response: Vector databases have emerged as a critical component in modern 
AI applications, enabling efficient similarity search across high-dimensional 
embeddings. When designing a RAG system, the choice of vector database 
significantly impacts retrieval quality and latency...
```

### Tips

- **Be specific**: "Draft a technical blog post about..." works better than "write about..."
- **Use your style**: The more data you have in Qdrant about your writing, the better the personalization
- **Context matters**: The RAG retrieves relevant examples of your writing style

## Configuration

### LLM Selection

**Local Development (Default):**
```python
# config.py
USE_LOCAL_LLM = True  # Uses OpenAI
OPENAI_MODEL_ID = "gpt-4o-mini"
```

**Production (SageMaker):**
```python
USE_LOCAL_LLM = False  # Uses fine-tuned model
MODEL_ID = "pauliusztin/LLMTwin-Llama-3.1-8B"
DEPLOYMENT_ENDPOINT_NAME = "twin"
```

### RAG Parameters

```python
# config.py
TOP_K = 5              # Retrieve top 5 documents
KEEP_TOP_K = 5         # Keep top 5 after reranking
EXPAND_N_QUERY = 5     # Expand to 5 query variations
```

Adjust in `.env` or `config.py`:

```bash
# Retrieve more context
TOP_K=10
KEEP_TOP_K=7

# Better query expansion
EXPAND_N_QUERY=3
```

### Token Limits

```bash
MAX_INPUT_TOKENS=1536   # Max prompt length
MAX_TOTAL_TOKENS=2048   # Max response length
```

## Troubleshooting

### "No vectors found in Qdrant"

```bash
# Run the full pipeline first to create vectors
# 1. Crawl data
cd src\data_crawling
poetry run python run_local_enhanced.py

# 2. Process with feature_pipeline
cd src\feature_pipeline
poetry run python run_local.py

# 3. Verify vectors exist
curl http://localhost:6333/collections
```

### "OpenAI API error"

```bash
# Check API key
echo $env:OPENAI_API_KEY  # Windows PowerShell
# or
echo $OPENAI_API_KEY      # Linux/Mac

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Common issues:
# - Invalid key
# - No credits
# - Rate limit exceeded
```

### "Qdrant connection failed"

```bash
# Check Qdrant is running
docker ps | grep qdrant

# Start if not running
docker-compose up qdrant -d

# Test connection
curl http://localhost:6333/healthz

# Check logs
docker logs llm-twin-qdrant
```

### "Poor response quality"

```bash
# 1. Check you have enough data
curl http://localhost:6333/collections

# Need at least 10-20 embedded articles for good results

# 2. Adjust RAG parameters
# Increase context:
TOP_K=10
KEEP_TOP_K=7

# 3. Use better LLM
OPENAI_MODEL_ID=gpt-4o  # Better but more expensive
```

### "Gradio port already in use"

```bash
# Change port in run_local_ui.py:
server_port=7861  # Or any other port

# Or kill existing process
# Windows:
netstat -ano | findstr :7860
taskkill /PID <pid> /F

# Linux/Mac:
lsof -ti:7860 | xargs kill -9
```

## Mock Mode (No API Calls)

For testing without OpenAI costs:

```python
# In run_local_ui.py
llm_twin = LLMTwin(mock=True)
```

Returns: `"Mocked answer."`

Useful for:
- Testing UI layout
- Testing RAG retrieval
- Debugging prompt construction
- CI/CD pipelines

## Development Workflow

### 1. Initial Setup

```bash
# Start Qdrant
docker-compose up qdrant -d

# Populate with data (full pipeline)
cd src\feature_pipeline
poetry run python run_local.py

# In another terminal, run data_cdc
cd src\data_cdc
poetry run python run_local.py
```

### 2. Test with CLI

```bash
cd src\inference_pipeline
poetry run python run_local.py
```

Review outputs, adjust prompts/RAG params.

### 3. Launch UI

```bash
poetry run python run_local_ui.py
```

Test interactively at http://localhost:7860

### 4. Iterate

- Edit `prompt_templates.py` for better prompts
- Adjust RAG params in `config.py`
- Add more data via `data_crawling`
- Rerun and test

## Customization

### Change Author Style

```python
# In run_local_ui.py, change default author:
gr.Textbox(
    "Your Name",  # Change this
    label="Who are you?",
)
```

### Modify Prompts

Edit `src/inference_pipeline/prompt_templates.py`:

```python
class InferenceTemplate:
    def create_template(self, enable_rag: bool = False):
        # Customize system prompt
        system_prompt = "You are a technical writer..."
        
        # Customize user prompt template
        if enable_rag:
            template = "Context: {context}\n\nQuestion: {question}"
        ...
```

### Add Custom Features

```python
# In run_local_ui.py

def predict(message: str, history: list, author: str, style: str):
    # Add style parameter
    query = f"I am {author}. Write in {style} style: {message}"
    ...

# Add to UI
additional_inputs=[
    gr.Textbox("Paul Iusztin", label="Who are you?"),
    gr.Dropdown(["Technical", "Casual", "Academic"], label="Style"),
]
```

## Performance

### Response Time

- **RAG Retrieval**: ~0.5-1s
- **OpenAI API**: ~2-10s (depends on response length)
- **Total**: ~3-12s per query

### Costs (OpenAI gpt-4o-mini)

- **Input**: ~$0.15 per 1M tokens
- **Output**: ~$0.60 per 1M tokens
- **Typical query**: ~1000 input + 500 output tokens = ~$0.0005 per query

Very affordable for development!

### Optimization

```python
# Faster but less context
TOP_K = 3
KEEP_TOP_K = 3

# Shorter responses
MAX_TOTAL_TOKENS = 1024

# Disable monitoring
# Comment out opik decorators in llm_twin.py
```

## Production Deployment

To use the fine-tuned model instead of OpenAI:

```python
# config.py
USE_LOCAL_LLM = False  # Use SageMaker

# Requires:
# - Fine-tuned model deployed to SageMaker
# - AWS credentials configured
# - DEPLOYMENT_ENDPOINT_NAME set correctly
```

Then run normally with `run_local_ui.py`.

## Next Steps

1. **Collect more data**: Run data_crawling on more of your content
2. **Fine-tune model**: Use training_pipeline with your data
3. **Deploy to SageMaker**: Host your fine-tuned model
4. **Switch to production**: Set USE_LOCAL_LLM=False
5. **Monitor**: Use Opik for tracking and evaluation

## Benefits

✅ **Local Development**: No SageMaker needed
✅ **Cost-Effective**: OpenAI gpt-4o-mini is very cheap
✅ **Fast Iteration**: Edit and test immediately
✅ **Full RAG Pipeline**: Same as production
✅ **Interactive UI**: Test with real conversations
✅ **Gradio**: Easy to customize and deploy
