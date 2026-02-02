"""
Extractors for shops and other data from HTML.
"""

import logging
from typing import List
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .models import Shop


logger = logging.getLogger(__name__)


class ShopExtractor:
    """Extractor for shop links from the sidebar menu."""
    
    def __init__(self, base_url: str):
        """
        Initialize extractor.
        
        Args:
            base_url: Base URL for resolving relative URLs
        """
        self.base_url = base_url
    
    def extract_shops(self, html: str) -> List[Shop]:
        """
        Extract all shop links from sidebar menu.
        
        Args:
            html: HTML content
            
        Returns:
            List of Shop objects
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the sidebar menu
        sidebar = soup.select_one('div#sidebar')
        if not sidebar:
            logger.warning("Sidebar not found")
            return []
        
        # Find all shop links
        shop_links = sidebar.select('ul#left-category-shops li a')
        
        shops = []
        for link in shop_links:
            name = link.get_text(strip=True)
            url = link.get('href')
            
            if not url:
                logger.warning(f"No URL found for shop: {name}")
                continue
            
            # Ensure absolute URL
            if not url.startswith('http'):
                url = urljoin(self.base_url, url)
            
            shop = Shop(name=name, url=url)
            shops.append(shop)
        
        logger.info(f"Found {len(shops)} shops in sidebar")
        return shops