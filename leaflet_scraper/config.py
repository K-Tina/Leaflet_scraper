"""
Configuration constants for the scraper.
"""

# URLs
BASE_URL = 'https://www.prospektmaschine.de'
HYPERMARKETS_URL = 'https://www.prospektmaschine.de/hypermarkte/'

# User Agent
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
)

# Scraping settings
DEFAULT_DELAY = 1.0  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds

# Date settings
OPEN_ENDED_DATE = '9999-12-31'

# German day names
GERMAN_DAYS = [
    'montag', 'dienstag', 'mittwoch', 'donnerstag',
    'freitag', 'samstag', 'sonntag'
]