#!/usr/bin/env python3
"""
Main entry point for the leaflet scraper.
"""

import logging

from leaflet_scraper import LeafletScraper, JSONExporter
from leaflet_scraper.exceptions import ScraperException


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Settings - change these values as needed
    debug = False
    output_file = 'leaflets.json'
    delay = 1.0
    
    try:
        logger.info("Starting leaflet scraper for all hypermarket chains")
        
        # Initialize scraper
        scraper = LeafletScraper(debug=debug, delay=delay)
        
        # Scrape all leaflets
        leaflets = scraper.scrape()
        
        if not leaflets:
            logger.error("No leaflets were found")
            return
        
        # Export to JSON
        exporter = JSONExporter()
        exporter.export(leaflets, output_file)
        
        logger.info(f"✓ Scraping completed successfully. Total leaflets: {len(leaflets)}")
        
    except ScraperException as e:
        logger.error(f"Scraping failed: {e}")
        raise
    except KeyboardInterrupt:
        logger.warning("Scraping interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()