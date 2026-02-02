"""
Exporters for saving data to JSON format.
"""

import json
import logging
from typing import List

from .models import Leaflet


logger = logging.getLogger(__name__)


class JSONExporter:
    """Export leaflets to JSON format."""
    
    @staticmethod
    def export(leaflets: List[Leaflet], filename: str, indent: int = 2) -> None:
        """
        Export leaflets to JSON file.
        
        Args:
            leaflets: List of Leaflet objects
            filename: Output filename
            indent: JSON indentation (default: 2)
            
        Raises:
            IOError: If file writing fails
        """
        try:
            data = [leaflet.to_dict() for leaflet in leaflets]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=indent)
            
            logger.info(f"Exported {len(leaflets)} leaflets to {filename}")
            
        except IOError as e:
            raise IOError(f"Failed to write JSON file: {e}")