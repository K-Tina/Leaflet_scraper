"""
Data models for leaflets and shops.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict

from .config import OPEN_ENDED_DATE
from .exceptions import ValidationException


@dataclass
class Leaflet:
    """Data model for a promotional leaflet."""
    title: str
    thumbnail: str
    shop_name: str
    valid_from: str  # Format: YYYY-MM-DD
    valid_to: str    # Format: YYYY-MM-DD (9999-12-31 for open-ended)
    parsed_time: str  # Format: YYYY-MM-DD HH:MM:SS
    
    def validate(self) -> bool:
        """
        Validate leaflet data consistency.
        
        Returns:
            bool: True if all fields are valid
            
        Raises:
            ValidationException: If any field is invalid
        """
        if not self.title or not self.title.strip():
            raise ValidationException("Title cannot be empty")
        
        if not self.thumbnail or not self.thumbnail.startswith('http'):
            raise ValidationException(f"Invalid thumbnail URL: {self.thumbnail}")
        
        if not self.shop_name or not self.shop_name.strip():
            raise ValidationException("Shop name cannot be empty")
        
        # Validate date formats
        try:
            datetime.strptime(self.valid_from, '%Y-%m-%d')
            datetime.strptime(self.valid_to, '%Y-%m-%d')
            datetime.strptime(self.parsed_time, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            raise ValidationException(f"Invalid date format: {e}")
        
        # Validate date logic (skip for open-ended leaflets)
        if self.valid_to != OPEN_ENDED_DATE:
            from_date = datetime.strptime(self.valid_from, '%Y-%m-%d')
            to_date = datetime.strptime(self.valid_to, '%Y-%m-%d')
            
            if from_date > to_date:
                raise ValidationException(
                    f"valid_from ({self.valid_from}) is after valid_to ({self.valid_to})"
                )
        
        return True
    
    def is_open_ended(self) -> bool:
        """Check if leaflet is open-ended."""
        return self.valid_to == OPEN_ENDED_DATE
    
    def to_dict(self) -> Dict:
        """Convert leaflet to dictionary."""
        return asdict(self)


@dataclass
class Shop:
    """Data model for a shop."""
    name: str
    url: str
    
    def __hash__(self):
        """Make Shop hashable for set operations."""
        return hash(self.url)
    
    def __eq__(self, other):
        """Compare shops by URL."""
        if not isinstance(other, Shop):
            return False
        return self.url == other.url