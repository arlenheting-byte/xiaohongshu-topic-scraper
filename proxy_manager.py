"""
Proxy manager for handling free proxies
"""
import requests
import logging
from typing import List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manage free proxies"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.proxies: List[str] = []
        self.proxy_index = 0
        self.last_update = None
        self.update_interval = timedelta(hours=1)
    
    def fetch_free_proxies(self) -> List[str]:
        """Fetch free proxies from public sources"""
        proxies = []
        
        # Source 1: proxy-list.download
        try:
            response = requests.get(
                'https://www.proxy-list.download/api/v1/get?type=http',
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'LISTA' in data:
                    proxy_list = data['LISTA'][:20]  # Get first 20
                    proxies.extend([f"http://{proxy}" for proxy in proxy_list])
                    logger.info(f"Fetched {len(proxy_list)} proxies from proxy-list.download")
        except Exception as e:
            logger.warning(f"Error fetching from proxy-list.download: {e}")
        
        # Source 2: Free Proxy List (simple format)
        try:
            response = requests.get(
                'https://www.sslproxies.org/',
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', {'class': 'table'})
                if table:
                    rows = table.tbody.find_all('tr')[:15]
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) > 1:
                            ip = cols[0].text.strip()
                            port = cols[1].text.strip()
                            proxy = f"http://{ip}:{port}"
                            proxies.append(proxy)
                    logger.info(f"Fetched {len(rows)} proxies from sslproxies.org")
        except Exception as e:
            logger.warning(f"Error fetching from sslproxies.org: {e}")
        
        # Source 3: GitHub raw proxy list
        try:
            response = requests.get(
                'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                timeout=self.timeout
            )
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                proxy_list = [f"http://{line}" for line in lines[:20] if line.strip()]
                proxies.extend(proxy_list)
                logger.info(f"Fetched {len(proxy_list)} proxies from GitHub")
        except Exception as e:
            logger.warning(f"Error fetching from GitHub: {e}")
        
        # Remove duplicates
        proxies = list(set(proxies))
        logger.info(f"Total unique proxies fetched: {len(proxies)}")
        return proxies
    
    def update_proxies(self, force: bool = False) -> bool:
        """Update proxy list"""
        if not force and self.last_update and \
           datetime.now() - self.last_update < self.update_interval:
            return True
        
        try:
            self.proxies = self.fetch_free_proxies()
            self.last_update = datetime.now()
            self.proxy_index = 0
            
            if self.proxies:
                logger.info(f"Successfully updated {len(self.proxies)} proxies")
                return True
            else:
                logger.warning("No proxies fetched")
                return False
        except Exception as e:
            logger.error(f"Error updating proxies: {e}")
            return False
    
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy in rotation"""
        if not self.proxies:
            self.update_proxies(force=True)
        
        if not self.proxies:
            logger.warning("No proxies available")
            return None
        
        proxy = self.proxies[self.proxy_index % len(self.proxies)]
        self.proxy_index += 1
        return proxy
    
    def test_proxy(self, proxy: str) -> bool:
        """Test if proxy is working"""
        try:
            response = requests.get(
                'http://httpbin.org/ip',
                proxies={'http': proxy, 'https': proxy},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Proxy {proxy} test failed: {e}")
            return False
    
    def get_working_proxy(self) -> Optional[str]:
        """Get a working proxy"""
        attempts = 0
        max_attempts = len(self.proxies) if self.proxies else 5
        
        while attempts < max_attempts:
            proxy = self.get_next_proxy()
            if proxy and self.test_proxy(proxy):
                logger.info(f"Using proxy: {proxy}")
                return proxy
            attempts += 1
        
        logger.warning("No working proxy found")
        return None
