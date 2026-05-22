"""
Configuration file for Xiaohongshu Topic Scraper
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'xiaohongshu_data.db')

# Scraper configuration
HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'
TIMEOUT = int(os.getenv('TIMEOUT', '30'))
RETRY_TIMES = int(os.getenv('RETRY_TIMES', '3'))

# Proxy configuration
USE_PROXY = os.getenv('USE_PROXY', 'True').lower() == 'true'
PROXY_TIMEOUT = int(os.getenv('PROXY_TIMEOUT', '10'))

# Request headers
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

# Xiaohongshu URLs
XIAOHONGSHU_BASE_URL = 'https://www.xiaohongshu.com'
SEARCH_TOPIC_URL = 'https://edith.xiaohongshu.com/web_api/feed'

# Free proxy sources
FREE_PROXY_SOURCES = [
    'https://www.proxy-list.download/api/v1/get?type=http',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
    'https://free-proxy-list.net/',
]

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
