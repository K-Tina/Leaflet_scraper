"""
Parsers for dates and leaflet HTML elements.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .config import GERMAN_DAYS, OPEN_ENDED_DATE
from .exceptions import ParsingException
from .models import Leaflet


logger = logging.getLogger(__name__)


class DateParser:
    """Parser for German date formats."""
    
    @staticmethod
    def parse_date_range(date_string: str, current_year: int = None) -> Tuple[str, str]:
        """
        Parse German date range format to ISO dates.
        
        Supported formats:
        - "02.02.2026 - 07.02.2026" (standard range)
        - "02.02. - 07.02.2026" (short format)
        - "von Mittwoch 01.10.2025" (open-ended, returns 9999-12-31 as end date)
        - "ab 01.10.2025" (open-ended)
        
        Args:
            date_string: Date range string in German format
            current_year: Year to use if not specified (default: current year)
            
        Returns:
            tuple: (valid_from, valid_to) in YYYY-MM-DD format
                   valid_to is '9999-12-31' for open-ended leaflets
            
        Raises:
            ParsingException: If date parsing fails
        """
        if current_year is None:
            current_year = datetime.now().year
        
        try:
            # Clean the string
            original_string = date_string
            date_string = date_string.strip()
            
            # Remove day names (Montag, Dienstag, etc.)
            for day in GERMAN_DAYS:
                date_string = re.sub(r'\b' + day + r'\b', '', date_string, flags=re.IGNORECASE)
            
            # Remove common prefixes
            date_string = re.sub(r'\b(von|ab|seit)\b', '', date_string, flags=re.IGNORECASE)
            date_string = date_string.strip()
            
            # Pattern 1: DD.MM.YYYY - DD.MM.YYYY
            pattern1 = r'(\d{2})\.(\d{2})\.(\d{4})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})'
            match = re.search(pattern1, date_string)
            
            if match:
                day1, month1, year1, day2, month2, year2 = match.groups()
                valid_from = f"{year1}-{month1}-{day1}"
                valid_to = f"{year2}-{month2}-{day2}"
                return valid_from, valid_to
            
            # Pattern 2: DD.MM. - DD.MM.YYYY
            pattern2 = r'(\d{2})\.(\d{2})\.\s*-\s*(\d{2})\.(\d{2})\.(\d{4})'
            match = re.search(pattern2, date_string)
            
            if match:
                day1, month1, day2, month2, year2 = match.groups()
                year1 = year2 if int(month1) <= int(month2) else str(int(year2) - 1)
                valid_from = f"{year1}-{month1}-{day1}"
                valid_to = f"{year2}-{month2}-{day2}"
                return valid_from, valid_to
            
            # Pattern 3: Single date DD.MM.YYYY (open-ended)
            pattern3 = r'(\d{2})\.(\d{2})\.(\d{4})'
            match = re.search(pattern3, date_string)
            
            if match:
                day, month, year = match.groups()
                valid_from = f"{year}-{month}-{day}"
                valid_to = OPEN_ENDED_DATE
                
                logger.info(f"Open-ended leaflet detected: '{original_string}' → {valid_from} to {valid_to}")
                return valid_from, valid_to
            
            raise ParsingException(f"Unsupported date format: {original_string}")
            
        except ParsingException:
            raise
        except Exception as e:
            raise ParsingException(f"Failed to parse date range '{original_string}': {e}")


class LeafletParser:
    """Parser for individual leaflet HTML elements."""
    
    def __init__(self, base_url: str, debug: bool = False):
        """
        Initialize parser.
        
        Args:
            base_url: Base URL for resolving relative URLs
            debug: Enable debug mode with detailed logging
        """
        self.base_url = base_url
        self.date_parser = DateParser()
        self.debug = debug
    
    def _extract_thumbnail(self, element: BeautifulSoup) -> Optional[str]:
        """
        Extract thumbnail URL with multiple fallback strategies.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            str: Thumbnail URL or None
        """
        # Strategy 1: Standard selector
        img_elem = element.select_one('div.image-wrapper picture img')
        
        if img_elem:
            # Try src attribute
            thumbnail = img_elem.get('src')
            if thumbnail:
                if self.debug:
                    logger.debug(f"Found thumbnail in 'src': {thumbnail}")
                return thumbnail
            
            # Try data-src (lazy loading)
            thumbnail = img_elem.get('data-src')
            if thumbnail:
                if self.debug:
                    logger.debug(f"Found thumbnail in 'data-src': {thumbnail}")
                return thumbnail
            
            # Try srcset
            srcset = img_elem.get('srcset')
            if srcset:
                # Extract first URL from srcset
                thumbnail = srcset.split(',')[0].split()[0]
                if self.debug:
                    logger.debug(f"Found thumbnail in 'srcset': {thumbnail}")
                return thumbnail
        
        # Strategy 2: Try without picture wrapper
        img_elem = element.select_one('div.image-wrapper img')
        if img_elem:
            thumbnail = img_elem.get('src') or img_elem.get('data-src')
            if thumbnail:
                if self.debug:
                    logger.debug(f"Found thumbnail without picture wrapper: {thumbnail}")
                return thumbnail
        
        # Strategy 3: Try any img in figure
        img_elem = element.select_one('figure img')
        if img_elem:
            thumbnail = img_elem.get('src') or img_elem.get('data-src')
            if thumbnail:
                if self.debug:
                    logger.debug(f"Found thumbnail in figure: {thumbnail}")
                return thumbnail
        
        # Debug: Print element structure if debugging is enabled
        if self.debug:
            logger.debug("Failed to find thumbnail. Element structure:")
            logger.debug(element.prettify()[:500])
        
        return None
    
    def parse(self, element: BeautifulSoup, shop_name: str = None, index: int = 0) -> Optional[Leaflet]:
        """
        Parse a single leaflet element.
        
        Args:
            element: BeautifulSoup element containing leaflet data
            shop_name: Override shop name from element
            index: Element index for debugging
            
        Returns:
            Leaflet object or None if parsing fails
        """
        try:
            if self.debug:
                logger.debug(f"\n{'='*60}\nParsing leaflet #{index}\n{'='*60}")
            
            # Extract title
            title_elem = element.select_one('h2')
            if not title_elem:
                logger.warning(f"Leaflet #{index}: Title element not found")
                return None
            title = title_elem.get_text(strip=True)
            
            if self.debug:
                logger.debug(f"Title: {title}")
            
            # Extract thumbnail with improved logic
            thumbnail = self._extract_thumbnail(element)
            
            if not thumbnail:
                logger.warning(f"Leaflet #{index} ({title}): Thumbnail image not found")
                if self.debug:
                    # Print available img tags
                    all_imgs = element.find_all('img')
                    logger.debug(f"Found {len(all_imgs)} img tags in element:")
                    for img in all_imgs:
                        logger.debug(f"  - {img.attrs}")
                return None
            
            # Ensure absolute URL
            if not thumbnail.startswith('http'):
                thumbnail = urljoin(self.base_url, thumbnail)
            
            if self.debug:
                logger.debug(f"Thumbnail: {thumbnail}")
            
            # Extract shop name (use override if provided)
            if not shop_name:
                shop_name_elem = element.select_one('span.shop-name')
                if not shop_name_elem:
                    logger.warning(f"Leaflet #{index}: Shop name element not found")
                    return None
                shop_name = shop_name_elem.get_text(strip=True)
            
            if self.debug:
                logger.debug(f"Shop: {shop_name}")
            
            # Extract date range
            # Try hidden-sm first (full format), then visible-sm
            date_elem = element.select_one('span.hidden-sm')
            if not date_elem or not date_elem.get_text(strip=True):
                date_elem = element.select_one('span.visible-sm')
            
            if not date_elem:
                logger.warning(f"Leaflet #{index}: Date element not found")
                return None
            
            date_string = date_elem.get_text(strip=True)
            
            if self.debug:
                logger.debug(f"Raw date string: {date_string}")
            
            valid_from, valid_to = self.date_parser.parse_date_range(date_string)
            
            if self.debug:
                logger.debug(f"Dates: {valid_from} to {valid_to}")
            
            # Current timestamp
            parsed_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create and validate leaflet object
            leaflet = Leaflet(
                title=title,
                thumbnail=thumbnail,
                shop_name=shop_name,
                valid_from=valid_from,
                valid_to=valid_to,
                parsed_time=parsed_time
            )
            
            leaflet.validate()
            
            if self.debug:
                logger.debug(f"✓ Successfully parsed leaflet #{index}")
            
            return leaflet
            
        except Exception as e:
            logger.error(f"Failed to parse leaflet #{index}: {e}")
            if self.debug:
                logger.exception(e)
            return None