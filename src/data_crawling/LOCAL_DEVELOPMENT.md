# Data Crawler - Local Development Guide

## Overview

This guide explains how to run the data crawler **locally** without Docker/Lambda, while keeping MongoDB in Docker.

## Architecture

```
┌─────────────────────────────────────┐
│  Your Local Machine                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Data Crawler (Python)        │  │
│  │ - run_local.py               │  │
│  │ - run_local_enhanced.py      │  │
│  └──────────┬───────────────────┘  │
│             │                       │
│             ↓ (localhost:30001-3)   │
│  ┌──────────────────────────────┐  │
│  │ Docker Containers            │  │
│  │ - MongoDB (replica set)      │  │
│  │   * mongo1:30001             │  │
│  │   * mongo2:30002             │  │
│  │   * mongo3:30003             │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Setup

### 1. Start MongoDB in Docker

```bash
# Start only MongoDB (not the full stack)
docker-compose up mongo1 mongo2 mongo3 -d

# Verify MongoDB is running
docker ps | grep mongo
```

### 2. Install Python Dependencies

```bash
# From project root
cd src/data_crawling
poetry install
```

### 3. Configure Python Environment

```bash
# Make sure your .env file is in the project root with MongoDB credentials
# The crawler will automatically patch settings to use localhost
```

## Running the Crawler

### Option 1: Simple Runner

```bash
cd src/data_crawling
poetry run python run_local.py
```

This will:
- Crawl a Medium article
- Crawl a GitHub repository
- Save data to MongoDB
- Show results

### Option 2: Enhanced Runner (Recommended)

```bash
cd src/data_crawling
poetry run python run_local_enhanced.py
```

This provides:
- Better bot detection avoidance (uses Selenium)
- Detailed logging and debugging
- Verification of saved data
- Content length validation

### Option 3: Custom Testing

```python
# Create your own test script
import sys
from pathlib import Path

ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

from data_crawling.config import settings
from data_crawling.main import handler

# Patch for local development
settings.patch_localhost()

# Test your own links
event = {
    "user": "Your Name",
    "link": "https://your-article-url.com"
}

result = handler(event, None)
print(result)
```

## Troubleshooting

### Issue: Bot Protection / Cloudflare

**Symptom**: Content shows "Just a moment..." or "Enable JavaScript"

**Solutions**:
1. Use `run_local_enhanced.py` which has better bot avoidance
2. Try different user agents
3. Add delays between requests
4. Some sites may require manual browser access first

### Issue: MongoDB Connection Failed

**Check**:
```bash
# Verify MongoDB is running
docker ps | grep mongo

# Test connection
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "rs.status()"
```

**Fix**: Make sure replica set is initialized:
```bash
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "rs.initiate({_id: 'my-replica-set', members: [{_id: 0, host: 'localhost:30001'}, {_id: 1, host: 'localhost:30002'}, {_id: 2, host: 'localhost:30003'}]})"
```

### Issue: No Data Saved

**Verify**:
```bash
# Check collections
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "use twin; show collections"

# Check articles
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "use twin; db.articles.find().pretty()"
```

### Issue: Import Errors

**Fix**:
```bash
# Make sure you're in the right directory
cd src/data_crawling

# Run with poetry
poetry run python run_local.py

# Or activate the environment
poetry shell
python run_local.py
```

## Viewing the Data

### MongoDB Compass

1. Connection string: `mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set`
2. Database: `twin`
3. Collections:
   - `users` - User documents
   - `articles` - Crawled articles
   - `posts` - LinkedIn posts
   - `repositories` - GitHub repositories

### MongoDB Shell

```bash
# Connect to MongoDB
docker exec -it llm-twin-mongo1 mongosh --port 30001

# Switch to twin database
use twin

# View collections
show collections

# Query articles
db.articles.find().pretty()

# Count documents
db.articles.countDocuments()

# Find specific article
db.articles.findOne({link: "https://medium.com/..."})
```

## Development Workflow

1. **Start MongoDB**: `docker-compose up mongo1 mongo2 mongo3 -d`
2. **Edit crawler code**: Make changes to files in `src/data_crawling/crawlers/`
3. **Test locally**: `poetry run python run_local_enhanced.py`
4. **Verify in DB**: Check MongoDB Compass or use mongosh
5. **Iterate**: Repeat steps 2-4 until satisfied
6. **Stop MongoDB**: `docker-compose down` (when done)

## Benefits of Local Development

✅ **Fast Iteration**: No Docker rebuild needed
✅ **Easy Debugging**: Use breakpoints, print statements
✅ **Quick Testing**: Test individual links without full stack
✅ **Instant Changes**: Edit code and rerun immediately
✅ **Full Control**: Customize crawler behavior easily

## Next Steps

Once data crawler is working locally:
1. Move to `data_cdc` (Change Data Capture)
2. Then `feature_pipeline` (Embeddings)
3. Keep all services as microservices
4. Only infrastructure (MongoDB, RabbitMQ, Qdrant) in Docker
