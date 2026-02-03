"""
Enhanced custom article crawler with better bot detection avoidance.

This version uses Selenium with stealth mode for better success rate.
"""

import time
from urllib.parse import urlparse

from aws_lambda_powertools import Logger
from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from crawlers.base import BaseCrawler
from core.db.documents import ArticleDocument

logger = Logger(service="llm-twin-course/crawler")


class EnhancedCustomArticleCrawler(BaseCrawler):
    model = ArticleDocument

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Article already exists in the database: {link}")
            return

        logger.info(f"Starting scrapping article with Selenium: {link}")

        driver = None
        try:
            # Use Selenium for better bot detection avoidance
            options = Options()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Set page load timeout
            options.page_load_strategy = 'eager'  # Don't wait for all resources
            
            logger.info("Initializing Chrome driver...")
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)  # 30 second timeout
            
            logger.info(f"Loading URL: {link}")
            driver.get(link)
            
            # Wait a bit for JavaScript to render
            time.sleep(3)
            
            # Get page source
            page_source = driver.page_source
            title = driver.title
            
            logger.info(f"Page loaded. Title: {title[:100]}")
            
            # Create document
            doc = Document(
                page_content=page_source,
                metadata={"title": title, "source": link}
            )
            
            # Transform HTML to text
            html2text = Html2TextTransformer()
            docs_transformed = html2text.transform_documents([doc])
            doc_transformed = docs_transformed[0]
            
            # Check content length
            content_length = len(doc_transformed.page_content)
            logger.info(f"Extracted content length: {content_length} characters")

            # Check if we got Cloudflare protection page
            content_text = doc_transformed.page_content.lower()
            if "just a moment" in content_text or "enable javascript" in content_text:
                logger.warning(f"Detected bot protection page for: {link}")
                logger.warning(f"Content preview: {doc_transformed.page_content[:200]}")
                return
            
            if content_length < 500:
                logger.warning(f"Content too short ({content_length} chars), might be blocked")
                logger.warning(f"Content preview: {doc_transformed.page_content[:200]}")
                return

            content = {
                "Title": doc_transformed.metadata.get("title", title),
                "Subtitle": doc_transformed.metadata.get("description", ""),
                "Content": doc_transformed.page_content,
                "language": doc_transformed.metadata.get("language", "en"),
            }

            parsed_url = urlparse(link)
            platform = parsed_url.netloc

            logger.info(f"Creating article document for platform: {platform}")
            instance = self.model(
                content=content,
                link=link,
                platform=platform,
                author_id=kwargs.get("user"),
            )
            
            logger.info("Saving to MongoDB...")
            saved_id = instance.save()
            if saved_id:
                logger.info(f"✓ Successfully saved article: {link} with ID: {saved_id}")
            else:
                logger.error(f"✗ Failed to save article: {link}")
                
        except Exception as e:
            logger.error(f"Error extracting article: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            
        finally:
            if driver:
                logger.info("Closing Chrome driver...")
                driver.quit()
