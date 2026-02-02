"""
Main scraper logic.
"""

import logging
import time
from typing import List

import requests
from bs4 import BeautifulSoup

from .config import BASE_URL, HYPERMARKETS_URL, USER_AGENT, DEFAULT_DELAY, REQUEST_TIMEOUT
from .exceptions import ScraperException, FetchException
from .extractors import ShopExtractor
from .models import Leaflet, Shop
from .parsers import LeafletParser


logger = logging.getLogger(__name__)


class LeafletScraper:
    """Main scraper class for prospektmaschine.de."""
    
    def __init__(self, debug: bool = False, delay: float = DEFAULT_DELAY):
        """
        Initialize scraper.
        
        Args:
            debug: Enable debug mode with detailed logging
            delay: Delay between requests in seconds
        """
        self.debug = debug
        self.delay = delay
        
        if debug:
            logger.setLevel(logging.DEBUG)
        
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
        
        self.leaflet_parser = LeafletParser(BASE_URL, debug=debug)
        self.shop_extractor = ShopExtractor(BASE_URL)
    
    def fetch_page(self, url: str) -> str:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            str: HTML content
            
        Raises:
            FetchException: If request fails
        """
        try:
            logger.info(f"Fetching page: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            if self.debug:
                logger.debug(f"Response status: {response.status_code}")
                logger.debug(f"Response length: {len(response.text)} characters")
            
            # Delay to be polite to the server
            if self.delay > 0:
                time.sleep(self.delay)
            
            return response.text
            
        except requests.RequestException as e:
            raise FetchException(f"Failed to fetch page: {e}")
    
    def extract_leaflets_from_page(self, html: str, shop_name: str = None) -> List[Leaflet]:
        """
        Extract all leaflets from HTML page.
        
        Args:
            html: HTML content
            shop_name: Override shop name for all leaflets
            
        Returns:
            List of Leaflet objects
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the main container
        container = soup.select_one('div.letaky-grid')
        if not container:
            logger.debug("Main container 'letaky-grid' not found")
            return []
        
        # Find all leaflet elements
        leaflet_elements = container.select('div.brochure-thumb.grid-item')
        
        if not leaflet_elements:
            logger.debug("No leaflet elements found")
            return []
        
        logger.debug(f"Found {len(leaflet_elements)} leaflet elements")
        
        leaflets = []
        for idx, element in enumerate(leaflet_elements, 1):
            leaflet = self.leaflet_parser.parse(element, shop_name=shop_name, index=idx)
            
            if leaflet:
                leaflets.append(leaflet)
        
        return leaflets
    
    def scrape_shop(self, shop: Shop) -> List[Leaflet]:
        """
        Scrape all leaflets from a single shop page.
        
        Args:
            shop: Shop object
            
        Returns:
            List of Leaflet objects
        """
        try:
            logger.info(f"Scraping shop: {shop.name}")
            html = self.fetch_page(shop.url)
            leaflets = self.extract_leaflets_from_page(html, shop_name=shop.name)
            
            # Count open-ended leaflets
            open_ended_count = sum(1 for l in leaflets if l.is_open_ended())
            regular_count = len(leaflets) - open_ended_count
            
            if open_ended_count > 0:
                logger.info(f"  → Found {len(leaflets)} leaflets for {shop.name} "
                          f"({regular_count} regular, {open_ended_count} open-ended)")
            else:
                logger.info(f"  → Found {len(leaflets)} leaflets for {shop.name}")
            
            return leaflets
            
        except Exception as e:
            logger.error(f"Failed to scrape shop {shop.name}: {e}")
            return []
    
    def scrape_all_shops(self) -> List[Leaflet]:
        """
        Scrape all leaflets from all shops.
        
        Returns:
            List of all Leaflet objects
            
        Raises:
            ScraperException: If scraping fails
        """
        # First, get the list of shops from the main hypermarkets page
        logger.info("Fetching shop list from hypermarkets page")
        html = self.fetch_page(HYPERMARKETS_URL)
        shops = self.shop_extractor.extract_shops(html)
        
        if not shops:
            raise ScraperException("No shops found in sidebar menu")
        
        logger.info(f"Starting to scrape {len(shops)} shops")
        
        # Scrape each shop
        all_leaflets = []
        successful_shops = 0
        failed_shops = 0
        open_ended_total = 0
        
        for idx, shop in enumerate(shops, 1):
            logger.info(f"\n[{idx}/{len(shops)}] Processing: {shop.name}")
            
            leaflets = self.scrape_shop(shop)
            
            if leaflets:
                all_leaflets.extend(leaflets)
                successful_shops += 1
                open_ended_total += sum(1 for l in leaflets if l.is_open_ended())
            else:
                failed_shops += 1
        
        regular_total = len(all_leaflets) - open_ended_total
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Scraping completed!")
        logger.info(f"Total shops processed: {len(shops)}")
        logger.info(f"Shops with leaflets: {successful_shops}")
        logger.info(f"Shops without leaflets: {failed_shops}")
        logger.info(f"Total leaflets collected: {len(all_leaflets)}")
        logger.info(f"  - Regular leaflets: {regular_total}")
        logger.info(f"  - Open-ended leaflets: {open_ended_total}")
        logger.info(f"{'='*60}\n")
        
        return all_leaflets
    
    def scrape(self) -> List[Leaflet]:
        """
        Main scraping method.
        
        Returns:
            List of all Leaflet objects
        """
        return self.scrape_all_shops()