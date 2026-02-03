from urllib.parse import urlparse

from aws_lambda_powertools import Logger
from core.db.documents import ArticleDocument
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers.html2text import Html2TextTransformer

from .base import BaseCrawler

logger = Logger(service="llm-twin-course/crawler")


class CustomArticleCrawler(BaseCrawler):
    model = ArticleDocument

    def __init__(self) -> None:
        super().__init__()

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        if old_model is not None:
            logger.info(f"Article already exists in the database: {link}")
            return

        logger.info(f"Starting scrapping article: {link}")

        try:
            # Add headers to avoid bot detection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            logger.info("Loading page with AsyncHtmlLoader...")
            loader = AsyncHtmlLoader([link], header_template=headers)
            docs = loader.load()
            
            if not docs or not docs[0].page_content:
                logger.warning(f"No content loaded from: {link}")
                return

            logger.info("Transforming HTML to text...")
            html2text = Html2TextTransformer()
            docs_transformed = html2text.transform_documents(docs)
            doc_transformed = docs_transformed[0]
            
            content_length = len(doc_transformed.page_content)
            logger.info(f"Extracted content length: {content_length} characters")
            
            # Check if we got bot protection page
            content_text = doc_transformed.page_content.lower()
            if "just a moment" in content_text or "enable javascript" in content_text:
                logger.warning(f"Detected bot protection page for: {link}")
                logger.warning(f"Content preview: {doc_transformed.page_content[:200]}")
                logger.info("Try using the enhanced crawler instead (use_enhanced=True)")
                return
            
            if content_length < 500:
                logger.warning(f"Content too short ({content_length} chars)")
                logger.warning(f"Content preview: {doc_transformed.page_content[:200]}")

            content = {
                "Title": doc_transformed.metadata.get("title", ""),
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
                logger.error(f"✗ Failed to save article to MongoDB")
                
        except Exception as e:
            logger.error(f"Error extracting article: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
