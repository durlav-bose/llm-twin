"""
Interactive local runner for data crawling with enhanced options.

This script provides better debugging and control for local development.

Usage:
    python run_local_enhanced.py
"""

import sys
from pathlib import Path

# Add src to path for imports
ROOT_DIR = str(Path(__file__).parent.parent)
sys.path.insert(0, ROOT_DIR)

from config import settings
from core import lib
from core.db.documents import UserDocument, ArticleDocument
from crawlers import CustomArticleCrawler, GithubCrawler, LinkedInCrawler
from crawlers.enhanced_custom_article import EnhancedCustomArticleCrawler
from dispatcher import CrawlerDispatcher

# Patch settings to use localhost for MongoDB
settings.patch_localhost()
print("="*80)
print("🚀 LLM Twin - Local Data Crawler")
print("="*80)
print(f"✓ MongoDB: {settings.MONGO_DATABASE_HOST}")
print(f"✓ Database: {settings.MONGO_DATABASE_NAME}")
print("="*80)

def crawl_link(user_name: str, link: str, use_enhanced: bool = False):
    """Crawl a single link and save to MongoDB."""
    
    print(f"\n📝 User: {user_name}")
    print(f"🔗 Link: {link}")
    print(f"🛠️  Enhanced Mode: {use_enhanced}")
    print("-" * 80)
    
    # Get or create user
    first_name, last_name = lib.split_user_full_name(user_name)
    user_id = UserDocument.get_or_create(first_name=first_name, last_name=last_name)
    print(f"✓ User ID: {user_id}")
    
    # Setup dispatcher
    _dispatcher = CrawlerDispatcher()
    
    if use_enhanced:
        _dispatcher.register("medium", EnhancedCustomArticleCrawler)
    else:
        _dispatcher.register("medium", CustomArticleCrawler)
    
    _dispatcher.register("linkedin", LinkedInCrawler)
    _dispatcher.register("github", GithubCrawler)
    
    # Get appropriate crawler
    crawler = _dispatcher.get_crawler(link)
    print(f"✓ Using crawler: {crawler.__class__.__name__}")
    
    # Extract content
    try:
        print(f"\n⏳ Starting extraction...")
        crawler.extract(link=link, user=user_id)
        print(f"✅ Extraction completed!")
        
        # Verify data was saved
        article = ArticleDocument.find(link=link)
        if article:
            print(f"✓ Article found in database:")
            print(f"  - ID: {article.id}")
            print(f"  - Platform: {article.platform}")
            print(f"  - Title: {article.content.get('Title', 'N/A')[:80]}")
            content_len = len(article.content.get('Content', ''))
            print(f"  - Content length: {content_len} characters")
            
            if content_len < 500:
                print(f"⚠️  WARNING: Content seems too short. Might be bot protection page.")
        else:
            print(f"⚠️  Article not found in database after crawling")
            
    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("-" * 80)


if __name__ == "__main__":
    # Test different articles
    test_cases = [
        {
            "user": "Paul Iusztin",
            "link": "https://medium.com/decodingml/an-end-to-end-framework-for-production-ready-llm-systems-by-building-your-llm-twin-2cc6bb01141f",
            "use_enhanced": True  # Try enhanced version for Medium
        },
        # Uncomment to test GitHub
        # {
        #     "user": "Paul Iusztin",
        #     "link": "https://github.com/decodingml/llm-twin-course",
        #     "use_enhanced": False
        # },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test Case {i}/{len(test_cases)}")
        print(f"{'='*80}")
        
        crawl_link(
            user_name=test_case["user"],
            link=test_case["link"],
            use_enhanced=test_case.get("use_enhanced", False)
        )
    
    print(f"\n{'='*80}")
    print("✅ All test cases completed!")
    print("\n📊 Check your data:")
    print("   - MongoDB Compass: mongodb://localhost:30001,localhost:30002,localhost:30003/?replicaSet=my-replica-set")
    print("   - Database: twin")
    print("   - Collections: users, articles")
    print("="*80)
