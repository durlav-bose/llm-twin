# Data CDC - Local Development Guide

## Overview

Data CDC (Change Data Capture) watches MongoDB for changes and publishes them to RabbitMQ.

## Architecture

```
┌────────────────────────────────────────────────────┐
│  Your Local Machine                                │
│                                                    │
│  ┌──────────────┐         ┌──────────────┐        │
│  │ data_cdc     │         │ Docker       │        │
│  │ (Python)     │────────→│              │        │
│  │              │  watch  │  MongoDB     │        │
│  │ run_local.py │←────────│  (30001-3)   │        │
│  └──────┬───────┘         │              │        │
│         │                 │  RabbitMQ    │        │
│         └────────────────→│  (5673)      │        │
│           publish         └──────────────┘        │
└────────────────────────────────────────────────────┘
```

## What It Does

1. **Watches** MongoDB change streams for inserts in:
   - `articles` collection
   - `posts` collection
   - `repositories` collection

2. **Transforms** the change event:
   - Extracts document data
   - Adds metadata (type, entry_id)
   - Serializes to JSON

3. **Publishes** to RabbitMQ:
   - Queue: `default`
   - For consumption by feature_pipeline

## Setup

### Prerequisites

```bash
# 1. MongoDB running (should already be running from data_crawling)
docker ps | grep mongo

# 2. RabbitMQ running
docker-compose up mq -d

# 3. Verify ports
docker ps | grep -E "mongo|mq"
# Should show:
#   - mongo1: 30001:30001
#   - mongo2: 30002:30002
#   - mongo3: 30003:30003
#   - mq: 5673:5672, 15673:15672
```

### Check Setup

```bash
cd src\data_cdc
poetry run python check_setup.py
```

This verifies:
- ✅ MongoDB connection
- ✅ RabbitMQ connection
- ✅ Database and collections exist
- ✅ Queue is accessible

## Running Locally

```bash
cd src\data_cdc
poetry run python run_local.py
```

You should see:
```
================================================================================
🚀 LLM Twin - Data CDC (Change Data Capture)
================================================================================
✓ MongoDB: mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set
✓ Database: twin
✓ RabbitMQ: localhost:5673
✓ Queue: default
================================================================================

📡 Watching MongoDB for changes...
   Supported collections: articles, posts, repositories
   Press Ctrl+C to stop
```

## Testing the CDC

### 1. Start data_cdc

```bash
# Terminal 1
cd src\data_cdc
poetry run python run_local.py
```

### 2. Insert data using data_crawling

```bash
# Terminal 2
cd src\data_crawling
poetry run python run_local_enhanced.py
```

### 3. Watch the CDC output

You should see in Terminal 1:
```
Change detected and serialized for a data sample of type articles.
Data of type 'articles' published to RabbitMQ.
```

### 4. Verify message in RabbitMQ

```bash
# Check RabbitMQ management UI
http://localhost:15673

# Or check queue via CLI
docker exec -it llm-twin-mq rabbitmqctl list_queues
```

## Troubleshooting

### "Connection refused" to MongoDB

```bash
# Check MongoDB is running
docker ps | grep mongo

# Start if not running
docker-compose up mongo1 mongo2 mongo3 -d

# Test connection
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "rs.status()"
```

### "Connection refused" to RabbitMQ

```bash
# Check RabbitMQ is running
docker ps | grep mq

# Start if not running
docker-compose up mq -d

# Check logs
docker logs llm-twin-mq
```

### No changes detected

```bash
# Make sure there's data in MongoDB
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "use twin; db.articles.find().pretty()"

# Insert test data
cd src\data_crawling
poetry run python run_local_enhanced.py
```

### "Unsupported data type" message

CDC only watches these collections:
- `articles`
- `posts`
- `repositories`

Other collections (like `users`) are ignored.

## How It Works

### MongoDB Change Streams

```python
# Watches for INSERT operations only
changes = db.watch([{"$match": {"operationType": {"$in": ["insert"]}}}])

for change in changes:
    # Process each insert
    ...
```

### Message Format

```json
{
  "type": "articles",
  "entry_id": "507f1f77bcf86cd799439011",
  "platform": "medium.com",
  "link": "https://medium.com/...",
  "content": {
    "Title": "...",
    "Content": "..."
  },
  "author_id": "..."
}
```

### RabbitMQ Publishing

```python
publish_to_rabbitmq(
    queue_name="default",
    data=json.dumps(document)
)
```

## Development Workflow

1. **Start infrastructure:**
   ```bash
   docker-compose up mongo1 mongo2 mongo3 mq -d
   ```

2. **Run data_cdc:**
   ```bash
   cd src\data_cdc
   poetry run python run_local.py
   ```

3. **Insert data** (in another terminal):
   ```bash
   cd src\data_crawling
   poetry run python run_local_enhanced.py
   ```

4. **See changes** detected in data_cdc terminal

5. **Stop with** `Ctrl+C`

## Next Steps

Once data_cdc is running and publishing messages:

1. Start feature_pipeline to consume and process messages
2. Check Qdrant for embedded vectors
3. Test the full pipeline: crawl → CDC → feature processing → vector storage
