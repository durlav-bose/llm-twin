# Local Data Crawler - Quick Start

## ✅ What You've Set Up

1. **`run_local.py`** - Simple local runner
2. **`run_local_enhanced.py`** - Enhanced runner with better debugging
3. **`LOCAL_DEVELOPMENT.md`** - Complete documentation
4. **`config.py`** - Updated with `patch_localhost()` method
5. **`crawlers/enhanced_custom_article.py`** - Better bot detection avoidance

## 🚀 How to Run

### Prerequisites

1. **Python 3.11** (required by the project):
   ```bash
   # Check your Python version
   python --version
   
   # If you have Python 3.11 installed, use poetry env:
   poetry env use python3.11
   # or
   poetry env use C:\Python311\python.exe  # Windows path to Python 3.11
   ```

2. **Chrome/Chromedriver** (for Selenium):
   - **Option 1**: Install Chrome browser (Selenium will auto-download chromedriver)
   - **Option 2**: Install via package manager:
     ```bash
     # Windows (using Chocolatey)
     choco install googlechrome
     
     # Or manually download Chrome from:
     # https://www.google.com/chrome/
     ```

3. **MongoDB running in Docker:**
   ```bash
   docker-compose up mongo1 mongo2 mongo3 -d
   ```

4. **Install Python dependencies:**
   ```bash
   cd D:\genesys\llm-and-ml\llm-twin
   
   # Use Python 3.11
   poetry env use python3.11
   
   # Install dependencies
   poetry install
   ```

### Run the Crawler

```bash
# First, verify your setup (recommended)
cd D:\genesys\llm-and-ml\llm-twin\src\data_crawling
poetry run python check_setup.py

# If all checks pass, run the crawler:

# Option 1: Simple runner
poetry run python run_local.py

# Option 2: Enhanced runner (better debugging)
poetry run python run_local_enhanced.py
```

### Or Using Virtual Environment

```bash
# Activate poetry environment
cd D:\genesys\llm-and-ml\llm-twin
poetry shell

# Run crawler
cd src\data_crawling
python run_local_enhanced.py
```

## 📊 Check the Data

### MongoDB Compass

- Connection: `mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set`
- Database: `twin`
- Collections: `users`, `articles`

### MongoDB Shell

```bash
docker exec -it llm-twin-mongo1 mongosh --port 30001 --eval "use twin; db.articles.find().pretty()"
```

## 🔧 Key Changes Made

### 1. **Config with localhost patch**

```python
# src/data_crawling/config.py
class Settings(BaseSettings):
    def patch_localhost(self) -> None:
        """Patch settings for local development outside Docker."""
        self.MONGO_DATABASE_HOST = "mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set"
        core_config.settings.patch_localhost()
```

### 2. **Enhanced Crawler**

The enhanced crawler uses Selenium with better headers to avoid bot detection:
- User agent spoofing
- Headless Chrome with stealth mode
- Better error handling
- Content validation

### 3. **Local Runners**

Both runners:
- Automatically patch settings to use `localhost` instead of Docker service names
- Connect to MongoDB in Docker on ports 30001-30003
- Provide detailed logging
- Verify data was saved

## 🐛 Troubleshooting

### "Current Python version is not allowed"

```bash
# The project requires Python 3.11
# Set the correct Python version:
poetry env use python3.11

# On Windows, use full path if needed:
poetry env use C:\Python311\python.exe

# Verify:
poetry env info

# Then install dependencies:
poetry install
```

### Chrome/Chromedriver Issues

```bash
# Make sure Chrome is installed
# Check Chrome version:
google-chrome --version  # Linux/Mac
# On Windows, check in: C:\Program Files\Google\Chrome\Application\chrome.exe

# If chromedriver errors occur:
# 1. Update Selenium: poetry add selenium@latest
# 2. Or manually install chromedriver matching your Chrome version
```

### "Module not found" error

```bash
# Make sure you installed dependencies
poetry install

# Or run with poetry prefix
poetry run python run_local_enhanced.py
```

### "Connection refused" to MongoDB

```bash
# Check MongoDB is running
docker ps | grep mongo

# Start if not running
docker-compose up mongo1 mongo2 mongo3 -d
```

### "Just a moment..." content

This means Cloudflare/bot protection kicked in. The enhanced crawler tries to avoid this, but some sites are heavily protected. For testing, try:
- Different articles/sites
- Adding delays
- Using the enhanced crawler

## ✨ Benefits

- ✅ No Docker rebuild needed for code changes
- ✅ Fast iteration and testing
- ✅ Easy debugging with breakpoints
- ✅ Immediate feedback
- ✅ Full control over crawler behavior

## 📝 Next Steps

After confirming this works:
1. Test with different article URLs
2. Customize the crawler as needed
3. Move to `data_cdc` for local development
4. Then `feature_pipeline`

All services will remain microservices, only infrastructure (MongoDB, RabbitMQ, Qdrant) stays in Docker.
