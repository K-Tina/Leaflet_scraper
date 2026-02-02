"""
Custom exceptions for the scraper.
"""


class ScraperException(Exception):
    """Base exception for scraper errors."""
    pass


class ParsingException(ScraperException):
    """Exception raised when parsing fails."""
    pass


class FetchException(ScraperException):
    """Exception raised when fetching page fails."""
    pass


class ValidationException(ScraperException):
    """Exception raised when validation fails."""
    pass