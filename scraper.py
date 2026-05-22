"""
Main Xiaohongshu topic scraper
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import time

from playwright.async_api import async_playwright, Browser, BrowserContext
from bs4 import BeautifulSoup
import requests

from config import (
    HEADLESS, TIMEOUT, RETRY_TIMES, USE_PROXY, 
    DEFAULT_HEADERS, XIAOHONGSHU_BASE_URL
)
from database import Database
from proxy_manager import ProxyManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class XiaohongshuScraper:
    """Main scraper class for Xiaohongshu"""
    
    def __init__(self, use_proxy: bool = USE_PROXY):
        self.db = Database()
        self.proxy_manager = ProxyManager() if use_proxy else None
        self.use_proxy = use_proxy
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def init_browser(self):
        """Initialize browser"""
        try:
            playwright = await async_playwright().start()
            
            launch_args = {
                'headless': HEADLESS,
                'args': [
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            }
            
            # Add proxy if available
            if self.use_proxy and self.proxy_manager:
                proxy = self.proxy_manager.get_next_proxy()
                if proxy:
                    launch_args['proxy'] = {'server': proxy}
                    logger.info(f"Browser initialized with proxy: {proxy}")
            
            self.browser = await playwright.chromium.launch(**launch_args)
            
            # Create context with user agent
            self.context = await self.browser.new_context(
                user_agent=DEFAULT_HEADERS['User-Agent']
            )
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing browser: {e}")
            raise
    
    async def close_browser(self):
        """Close browser"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def search_topic(self, topic: str, page: int = 1) -> List[Dict[str, Any]]:
        """Search and scrape notes for a topic"""
        try:
            page_obj = await self.context.new_page()
            
            # Set extra HTTP headers
            await page_obj.set_extra_http_headers(DEFAULT_HEADERS)
            
            # Navigate to search page
            search_url = f"{XIAOHONGSHU_BASE_URL}/search_result?keyword={topic}&type=general"
            logger.info(f"Navigating to: {search_url}")
            
            await page_obj.goto(search_url, wait_until='networkidle', timeout=TIMEOUT * 1000)
            
            # Wait for content to load
            await page_obj.wait_for_selector('[class*="feed"]', timeout=TIMEOUT * 1000)
            
            # Extract notes data
            notes = await self.extract_notes_data(page_obj, topic)
            
            await page_obj.close()
            return notes
        
        except Exception as e:
            logger.error(f"Error searching topic {topic}: {e}")
            return []
    
    async def extract_notes_data(self, page_obj, topic: str) -> List[Dict[str, Any]]:
        """Extract notes data from page"""
        try:
            # Get page content
            content = await page_obj.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            notes = []
            
            # Find note elements
            note_items = soup.find_all('div', {'class': lambda x: x and 'note-card' in x})
            
            for idx, item in enumerate(note_items, 1):
                try:
                    note_data = self.parse_note_item(item, topic, idx)
                    if note_data:
                        notes.append(note_data)
                except Exception as e:
                    logger.warning(f"Error parsing note item: {e}")
                    continue
            
            logger.info(f"Extracted {len(notes)} notes for topic: {topic}")
            return notes
        
        except Exception as e:
            logger.error(f"Error extracting notes data: {e}")
            return []
    
    def parse_note_item(self, item, topic: str, rank: int) -> Optional[Dict[str, Any]]:
        """Parse individual note item"""
        try:
            # Extract note ID
            note_id_elem = item.find('a', {'href': lambda x: x and '/note/' in x})
            note_id = None
            url = None
            
            if note_id_elem and note_id_elem.get('href'):
                url = note_id_elem['href']
                note_id = url.split('/note/')[-1].split('?')[0]
            
            if not note_id:
                return None
            
            # Extract title
            title_elem = item.find('h2') or item.find('h3')
            title = title_elem.text.strip() if title_elem else "N/A"
            
            # Extract content/description
            desc_elem = item.find('p', {'class': lambda x: x and 'desc' in x})
            content = desc_elem.text.strip() if desc_elem else title
            
            # Extract author
            author_elem = item.find('a', {'class': lambda x: x and 'author' in x})
            author = author_elem.text.strip() if author_elem else "Unknown"
            
            # Extract engagement metrics
            likes_count = self.extract_metric(item, 'like')
            comments_count = self.extract_metric(item, 'comment')
            collections_count = self.extract_metric(item, 'collect')
            shares_count = self.extract_metric(item, 'share')
            
            # Extract publish time
            time_elem = item.find('span', {'class': lambda x: x and 'time' in x})
            publish_time = time_elem.text.strip() if time_elem else datetime.now().isoformat()
            
            note_data = {
                'id': note_id,
                'topic': topic,
                'title': title,
                'content': content,
                'author': author,
                'publish_time': publish_time,
                'likes_count': likes_count,
                'comments_count': comments_count,
                'collections_count': collections_count,
                'shares_count': shares_count,
                'url': url,
                'rank_position': rank
            }
            
            return note_data
        
        except Exception as e:
            logger.warning(f"Error parsing note item: {e}")
            return None
    
    def extract_metric(self, item, metric_type: str) -> int:
        """Extract engagement metric"""
        try:
            metric_elem = item.find('span', {'class': lambda x: x and metric_type in x})
            if metric_elem:
                text = metric_elem.text.strip()
                # Remove common suffixes (万, K, etc.)
                if '万' in text:
                    return int(float(text.replace('万', '')) * 10000)
                elif 'K' in text:
                    return int(float(text.replace('K', '')) * 1000)
                else:
                    return int(''.join(c for c in text if c.isdigit()) or 0)
            return 0
        except Exception as e:
            logger.debug(f"Error extracting {metric_type} metric: {e}")
            return 0
    
    async def scrape_topic_ranking(self, topic: str) -> bool:
        """Scrape and save topic ranking"""
        try:
            logger.info(f"Starting to scrape topic: {topic}")
            
            # Record topic
            self.db.record_topic(topic)
            
            # Scrape notes
            notes = await self.search_topic(topic)
            
            if not notes:
                logger.warning(f"No notes found for topic: {topic}")
                return False
            
            # Save notes to database
            for note in notes:
                self.db.insert_note(note)
                
                # Save ranking
                ranking_data = {
                    'topic': topic,
                    'note_id': note['id'],
                    'rank_position': note['rank_position'],
                    'likes_count': note['likes_count'],
                    'comments_count': note['comments_count'],
                    'collections_count': note['collections_count'],
                    'publish_time': note['publish_time'],
                    'scraped_date': datetime.now().date().isoformat()
                }
                self.db.insert_ranking(ranking_data)
            
            # Update scrape time
            self.db.update_topic_scrape_time(topic)
            
            logger.info(f"Successfully scraped {len(notes)} notes for topic: {topic}")
            return True
        
        except Exception as e:
            logger.error(f"Error scraping topic {topic}: {e}")
            return False
    
    async def run(self, topics: List[str]):
        """Run scraper for multiple topics"""
        try:
            await self.init_browser()
            
            for topic in topics:
                try:
                    success = await self.scrape_topic_ranking(topic)
                    if success:
                        logger.info(f"✓ Successfully scraped: {topic}")
                    else:
                        logger.warning(f"✗ Failed to scrape: {topic}")
                    
                    # Add delay between requests
                    await asyncio.sleep(2)
                
                except Exception as e:
                    logger.error(f"Error processing topic {topic}: {e}")
                    continue
            
            await self.close_browser()
            logger.info("Scraping completed")
        
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            await self.close_browser()
            raise

async def main():
    """Main entry point"""
    # Example topics to scrape
    topics = [
        '穿搭',
        '护肤',
        '美食',
    ]
    
    scraper = XiaohongshuScraper(use_proxy=USE_PROXY)
    
    try:
        await scraper.run(topics)
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
