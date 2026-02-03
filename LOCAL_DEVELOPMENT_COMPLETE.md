# LLM Twin - Complete Local Development Setup

## Overview

All three microservices running **locally** with infrastructure in **Docker**.

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  Your Local Machine                                                │
│                                                                    │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐      │
│  │ data_        │     │ data_cdc     │     │ feature_     │      │
│  │ crawling     │     │              │     │ pipeline     │      │
│  │ (Python)     │     │ (Python)     │     │ (Python)     │      │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘      │
│         │                    │                    │              │
│         ↓                    ↓                    ↓              │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  Docker Infrastructure                                  │     │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │     │
│  │  │ MongoDB  │  │ RabbitMQ │  │ Qdrant   │             │     │
│  │  │ (3 nodes)│  │          │  │          │             │     │
│  │  │ :30001-3 │  │ :5673    │  │ :6333    │             │     │
│  │  └──────────┘  └──────────┘  └──────────┘             │     │
│  └─────────────────────────────────────────────────────────┘     │
└────────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
1. Data Crawling
   ├─ Crawls: Medium, LinkedIn, GitHub
   └─ Stores: MongoDB → users, articles, posts, repositories

2. Data CDC (Change Data Capture)
   ├─ Watches: MongoDB change streams
   └─ Publishes: RabbitMQ → queue "default"

3. Feature Pipeline
   ├─ Consumes: RabbitMQ
   ├─ Processes: Clean → Chunk → Embed
   └─ Stores: Qdrant → cleaned_documents, vector_documents
```

## Quick Start

### 1. Start Infrastructure (Docker)

```bash
# Start all infrastructure services
docker-compose up mongo1 mongo2 mongo3 mq qdrant -d

# Verify all running
docker ps

# Should see:
#   - llm-twin-mongo1 (30001:30001)
#   - llm-twin-mongo2 (30002:30002)
#   - llm-twin-mongo3 (30003:30003)
#   - llm-twin-mq (5673:5672, 15673:15672)
#   - llm-twin-qdrant (6333:6333)
```

### 2. Setup Python Environment

```bash
cd D:\genesys\llm-and-ml\llm-twin

# Use Python 3.11
poetry env use python3.11

# Install dependencies
poetry install
```

### 3. Verify Setup

```bash
# Check data_crawling
cd src\data_crawling
poetry run python check_setup.py

# Check data_cdc
cd ..\data_cdc
poetry run python check_setup.py

# Check feature_pipeline
cd ..\feature_pipeline
poetry run python check_setup.py
```

### 4. Run Services (3 Terminals)

**Terminal 1: Feature Pipeline**
```bash
cd D:\genesys\llm-and-ml\llm-twin\src\feature_pipeline
poetry run python run_local.py
```

**Terminal 2: Data CDC**
```bash
cd D:\genesys\llm-and-ml\llm-twin\src\data_cdc
poetry run python run_local.py
```

**Terminal 3: Data Crawling (Test)**
```bash
cd D:\genesys\llm-and-ml\llm-twin\src\data_crawling
poetry run python run_local_enhanced.py
```

### 5. Watch the Magic Happen!

```
Terminal 3 (crawler):
  ✓ Crawled article from Medium
  ✓ Saved to MongoDB

Terminal 2 (data_cdc):
  ✓ Detected MongoDB insert
  ✓ Published to RabbitMQ

Terminal 1 (feature_pipeline):
  ✓ Consumed from RabbitMQ
  ✓ Cleaned text
  ✓ Chunked into pieces
  ✓ Generated embeddings
  ✓ Stored in Qdrant
```

## Service Details

### data_crawling

- **Port**: None (runs locally)
- **Dependencies**: MongoDB (Docker)
- **Documentation**: [src/data_crawling/LOCAL_DEVELOPMENT.md](../src/data_crawling/LOCAL_DEVELOPMENT.md)
- **Setup Checker**: `python check_setup.py`
- **Run**: `poetry run python run_local_enhanced.py`

### data_cdc

- **Port**: None (runs locally)
- **Dependencies**: MongoDB, RabbitMQ (Docker)
- **Documentation**: [src/data_cdc/LOCAL_DEVELOPMENT.md](../src/data_cdc/LOCAL_DEVELOPMENT.md)
- **Setup Checker**: `python check_setup.py`
- **Run**: `poetry run python run_local.py`

### feature_pipeline

- **Port**: None (runs locally)
- **Dependencies**: RabbitMQ, Qdrant (Docker)
- **Documentation**: [src/feature_pipeline/LOCAL_DEVELOPMENT.md](../src/feature_pipeline/LOCAL_DEVELOPMENT.md)
- **Setup Checker**: `python check_setup.py`
- **Run**: `poetry run python run_local.py`

## Infrastructure Services (Docker)

### MongoDB

- **Ports**: 30001, 30002, 30003
- **Type**: Replica Set (3 nodes)
- **Database**: twin
- **Collections**: users, articles, posts, repositories
- **UI**: Use MongoDB Compass
  ```
  mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set
  ```

### RabbitMQ

- **Port**: 5673 (AMQP)
- **Management UI**: http://localhost:15673
- **Credentials**: guest/guest
- **Queue**: default

### Qdrant

- **Port**: 6333 (API)
- **Dashboard**: http://localhost:6333/dashboard
- **Collections**: 
  - cleaned_documents (non-vector)
  - vector_documents (embeddings)

## Common Commands

### Start Everything

```bash
# Infrastructure
docker-compose up mongo1 mongo2 mongo3 mq qdrant -d

# Services (3 terminals)
poetry run python src/feature_pipeline/run_local.py
poetry run python src/data_cdc/run_local.py
poetry run python src/data_crawling/run_local_enhanced.py
```

### Stop Everything

```bash
# Stop Python services: Ctrl+C in each terminal

# Stop infrastructure
docker-compose down

# Or keep data volumes
docker-compose stop
```

### Check Status

```bash
# Docker containers
docker ps

# RabbitMQ queues
docker exec -it llm-twin-mq rabbitmqctl list_queues

# MongoDB collections
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "use twin; show collections"

# Qdrant collections
curl http://localhost:6333/collections
```

### View Logs

```bash
# MongoDB
docker logs llm-twin-mongo1

# RabbitMQ
docker logs llm-twin-mq

# Qdrant
docker logs llm-twin-qdrant
```

## Troubleshooting

### Port Conflicts

```bash
# Check what's using ports
netstat -ano | findstr ":30001"
netstat -ano | findstr ":5673"
netstat -ano | findstr ":6333"

# Stop conflicting services or change ports in docker-compose.yml
```

### Python Version Mismatch

```bash
# Project requires Python 3.11
poetry env use python3.11
poetry install
```

### MongoDB Replica Set Not Initialized

```bash
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "rs.status()"

# If not initialized:
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "rs.initiate({_id: 'my-replica-set', members: [{_id: 0, host: 'localhost:30001'}, {_id: 1, host: 'localhost:30002'}, {_id: 2, host: 'localhost:30003'}]})"
```

### No Data Flowing

```bash
# 1. Check infrastructure is running
docker ps

# 2. Check services are running (in terminals)

# 3. Test manually:
#    - Run crawler first to create data
#    - Check MongoDB has data
#    - Check RabbitMQ has messages
#    - Check Qdrant has vectors
```

## Development Workflow

### Daily Development

1. **Start infrastructure**:
   ```bash
   docker-compose up mongo1 mongo2 mongo3 mq qdrant -d
   ```

2. **Code changes in your IDE**

3. **Test immediately**:
   ```bash
   # No Docker rebuild needed!
   poetry run python run_local.py
   ```

4. **Iterate fast**:
   - Edit code
   - Rerun script
   - See results instantly

### Adding Features

1. Edit code in `src/<service>/`
2. Test locally with `run_local.py`
3. Verify data in MongoDB/RabbitMQ/Qdrant
4. Commit when working

### Debugging

1. Add breakpoints in your IDE
2. Run with debugger attached
3. Step through code
4. Inspect variables
5. Fix issues immediately

## Performance Tips

### Faster Embeddings

```bash
# Use GPU if available (requires CUDA)
# Edit .env:
EMBEDDING_MODEL_DEVICE=cuda
```

### Parallel Processing

```bash
# Run multiple feature_pipeline instances
# Terminal 1
poetry run python run_local.py

# Terminal 2  
poetry run python run_local.py

# RabbitMQ will distribute messages
```

### Batch Size

```python
# Edit src/feature_pipeline/data_logic/dispatchers.py
# Increase batch size for embeddings
```

## Next Steps

### 1. Test Retrieval

```bash
cd src/feature_pipeline
poetry run python retriever.py
```

### 2. Generate Dataset

```bash
cd src/feature_pipeline/generate_dataset
poetry run python main.py
```

### 3. Training Pipeline

```bash
cd src/training_pipeline
poetry run python finetune.py
```

### 4. Inference Pipeline

```bash
cd src/inference_pipeline
poetry run python ui.py
```

## Benefits of This Setup

✅ **Fast Iteration**: No Docker rebuilds
✅ **Easy Debugging**: Use IDE breakpoints
✅ **Full Control**: Modify code instantly
✅ **Microservices**: Each service independent
✅ **Production-Like**: Same architecture as deployment
✅ **Cost-Effective**: No cloud costs during development

## File Structure

```
src/
├── data_crawling/
│   ├── run_local.py          ← Run crawler locally
│   ├── run_local_enhanced.py ← Enhanced crawler
│   ├── check_setup.py        ← Verify setup
│   ├── LOCAL_DEVELOPMENT.md  ← Full docs
│   └── QUICKSTART.md         ← Quick guide
│
├── data_cdc/
│   ├── run_local.py          ← Run CDC locally
│   ├── check_setup.py        ← Verify setup
│   └── LOCAL_DEVELOPMENT.md  ← Full docs
│
└── feature_pipeline/
    ├── run_local.py          ← Run pipeline locally
    ├── check_setup.py        ← Verify setup
    └── LOCAL_DEVELOPMENT.md  ← Full docs
```

## Support

Each service has:
- `run_local.py` - Local runner
- `check_setup.py` - Setup verification
- `LOCAL_DEVELOPMENT.md` - Detailed documentation
- Configuration with `patch_localhost()` method

All services work together seamlessly!
