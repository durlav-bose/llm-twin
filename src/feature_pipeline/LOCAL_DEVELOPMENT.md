# Feature Pipeline - Local Development Guide

## Overview

The feature pipeline consumes messages from RabbitMQ, processes them (cleaning, chunking, embedding), and stores the results in Qdrant vector database.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Your Local Machine                                      │
│                                                          │
│  ┌────────────────┐         ┌──────────────┐            │
│  │ Docker         │         │ feature_     │            │
│  │                │         │ pipeline     │            │
│  │ RabbitMQ       │────────→│ (Python)     │            │
│  │ (5673)         │ consume │              │            │
│  └────────────────┘         │ run_local.py │            │
│                             └──────┬───────┘            │
│  ┌────────────────┐                │                    │
│  │ Docker         │                │ store              │
│  │                │←───────────────┘                    │
│  │ Qdrant         │  embeddings                         │
│  │ (6333)         │                                      │
│  └────────────────┘                                      │
└──────────────────────────────────────────────────────────┘
```

## Processing Pipeline

```
RabbitMQ Message
    ↓
1. Raw Dispatch (parse message)
    ↓
2. Clean Dispatch (clean text)
    ↓
3. Store cleaned data → Qdrant (non-vector collection)
    ↓
4. Chunk Dispatch (split into chunks)
    ↓
5. Embedding Dispatch (generate vectors)
    ↓
6. Store embeddings → Qdrant (vector collection)
```

## Setup

### Prerequisites

```bash
# 1. RabbitMQ running
docker-compose up mq -d

# 2. Qdrant running
docker-compose up qdrant -d

# 3. Verify ports
docker ps | grep -E "mq|qdrant"
# Should show:
#   - mq: 5673:5672, 15673:15672
#   - qdrant: 6333:6333, 6334:6334
```

### Check Setup

```bash
cd src\feature_pipeline
poetry run python check_setup.py
```

This verifies:
- ✅ Python dependencies installed
- ✅ RabbitMQ connection
- ✅ Qdrant connection  
- ✅ Embedding model can be loaded

## Running Locally

```bash
cd src\feature_pipeline
poetry run python run_local.py
```

You should see:
```
================================================================================
🚀 LLM Twin - Feature Pipeline
================================================================================
✓ RabbitMQ: localhost:5673
✓ Queue: default
✓ Qdrant: localhost:6333
✓ Embedding Model: BAAI/bge-small-en-v1.5
✓ Embedding Size: 384
================================================================================

📊 Processing Pipeline:
   1. Consume from RabbitMQ
   2. Clean data
   3. Chunk into smaller pieces
   4. Generate embeddings
   5. Store in Qdrant

   Press Ctrl+C to stop

⏳ Starting Bytewax dataflow...
   Waiting for messages from RabbitMQ...
```

## Full Pipeline Test

### Terminal 1: Start feature_pipeline

```bash
cd src\feature_pipeline
poetry run python run_local.py
```

### Terminal 2: Start data_cdc

```bash
cd src\data_cdc  
poetry run python run_local.py
```

### Terminal 3: Insert data

```bash
cd src\data_crawling
poetry run python run_local_enhanced.py
```

### Expected Flow:

```
Terminal 3 (crawler):
  → Crawls article from Medium
  → Saves to MongoDB

Terminal 2 (data_cdc):
  → Detects MongoDB insert
  → Publishes to RabbitMQ

Terminal 1 (feature_pipeline):
  → Consumes from RabbitMQ
  → Cleans text
  → Chunks into pieces
  → Generates embeddings
  → Stores in Qdrant
```

## Verify Results in Qdrant

### Using Qdrant Web UI

```bash
# Open in browser
http://localhost:6333/dashboard

# You should see collections:
# - cleaned_documents (non-vector)
# - vector_documents (with embeddings)
```

### Using Python

```python
from qdrant_client import QdrantClient

client = QdrantClient(host='localhost', port=6333)

# List collections
collections = client.get_collections()
for c in collections.collections:
    info = client.get_collection(c.name)
    print(f"{c.name}: {info.points_count} points")

# Search for similar content
results = client.search(
    collection_name="vector_documents",
    query_vector=[0.1] * 384,  # dummy vector
    limit=5
)
```

## Troubleshooting

### "No messages in RabbitMQ"

```bash
# Make sure data_cdc is running and publishing
cd src\data_cdc
poetry run python run_local.py

# Insert test data
cd src\data_crawling
poetry run python run_local_enhanced.py
```

### "Failed to connect to Qdrant"

```bash
# Check Qdrant is running
docker ps | grep qdrant

# Start if not running
docker-compose up qdrant -d

# Check logs
docker logs llm-twin-qdrant

# Test connection
curl http://localhost:6333/collections
```

### "Embedding model download failed"

The model (`BAAI/bge-small-en-v1.5`) will be downloaded on first use (~130MB).

```bash
# Make sure you have internet connection
# Check disk space (need ~500MB for model cache)

# Model will be cached in:
# Windows: C:\Users\<user>\.cache\huggingface\
# Linux: ~/.cache/huggingface/
```

### "Bytewax dataflow error"

```bash
# Check all dependencies installed
poetry install

# Verify Bytewax version
poetry show bytewax

# Check Python version (should be 3.11)
python --version
```

## Configuration

### Embedding Model

Default: `BAAI/bge-small-en-v1.5` (384 dimensions)

To use different model:

```bash
# Edit .env file
EMBEDDING_MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_SIZE=384  # Update based on model
```

### Chunking Settings

Located in `src/feature_pipeline/data_logic/splitters.py`:

```python
# Default chunk size: 500 characters
# Default overlap: 50 characters
```

### OpenAI (Optional)

For query expansion and reranking:

```bash
# Add to .env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL_ID=gpt-4o-mini
```

## Development Workflow

1. **Start infrastructure:**
   ```bash
   docker-compose up mongo1 mongo2 mongo3 mq qdrant -d
   ```

2. **Run services** (separate terminals):
   ```bash
   # Terminal 1: Feature Pipeline
   cd src\feature_pipeline
   poetry run python run_local.py

   # Terminal 2: Data CDC
   cd src\data_cdc
   poetry run python run_local.py
   ```

3. **Test with data:**
   ```bash
   # Terminal 3: Data Crawler
   cd src\data_crawling
   poetry run python run_local_enhanced.py
   ```

4. **Verify in Qdrant:**
   ```bash
   http://localhost:6333/dashboard
   ```

5. **Stop services:**
   - Press `Ctrl+C` in each terminal

## Performance

- **Throughput**: ~10-50 documents/second (depends on document size)
- **Embedding**: ~100-200 chunks/second on CPU
- **Memory**: ~1-2GB for embedding model

To improve:
- Use GPU for embeddings (set `EMBEDDING_MODEL_DEVICE=cuda`)
- Increase batch size in embedding dispatcher
- Scale horizontally (run multiple feature_pipeline instances)

## Next Steps

Once feature_pipeline is working:

1. Test retrieval with `src/feature_pipeline/retriever.py`
2. Build RAG applications using the embedded vectors
3. Fine-tune the LLM using the training_pipeline
4. Deploy inference_pipeline for generating responses
