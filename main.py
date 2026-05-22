"""
Entry point for Xiaohongshu Topic Scraper
"""
import asyncio
import logging
import argparse
from datetime import datetime

from scraper import XiaohongshuScraper
from config import LOG_LEVEL

# Setup logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Xiaohongshu Topic Notes Hotness Ranking Scraper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py -t "穿搭"
  python main.py -t "穿搭" "护肤" "美食"
  python main.py -t "穿搭" --no-proxy
        '''
    )
    
    parser.add_argument(
        '-t', '--topics',
        nargs='+',
        required=True,
        help='Topics to scrape (e.g., "穿搭" "护肤")'
    )
    
    parser.add_argument(
        '--no-proxy',
        action='store_true',
        help='Disable proxy usage'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()

async def main():
    """Main function"""
    args = parse_arguments()
    
    logger.info("=" * 50)
    logger.info("Xiaohongshu Topic Scraper Started")
    logger.info("=" * 50)
    logger.info(f"Topics to scrape: {', '.join(args.topics)}")
    logger.info(f"Use proxy: {not args.no_proxy}")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)
    
    try:
        scraper = XiaohongshuScraper(use_proxy=not args.no_proxy)
        await scraper.run(args.topics)
        
        logger.info("=" * 50)
        logger.info("Scraping Completed Successfully!")
        logger.info(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 50)
        
    except KeyboardInterrupt:
        logger.info("\n✗ Scraping interrupted by user")
    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
        raise

if __name__ == '__main__':
    asyncio.run(main())
