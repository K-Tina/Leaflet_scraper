# Leaflet Scraper for prospektmaschine.de

Web scraper for extracting promotional leaflets from German hypermarket chains.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic usage
```bash
python main.py
```

This will:
- Scrape all 40+ hypermarket chains from prospektmaschine.de
- Export results to `leaflets.json`
- Use 1 second delay between requests

### Changing settings

Edit the settings directly in `main.py`:

```python
def main():
    """Main entry point."""
    # Settings - change these values as needed
    debug = False              # Set to True for detailed logging
    output_file = 'leaflets.json'  # Change output filename
    delay = 1.0               # Delay between requests in seconds
```

## Output Format

The scraper's output is a JSON file with the following structure:

```json
[
  {
    "title": "Prospekt",
    "thumbnail": "https://eu.leafletscdns.com/thumbor/...",
    "shop_name": "Aldi",
    "valid_from": "2026-02-02",
    "valid_to": "2026-02-08",
    "parsed_time": "2026-02-01 20:00:00"
  },
  {
    "title": "Edna Foodservice",
    "thumbnail": "https://eu.leafletscdns.com/thumbor/...",
    "shop_name": "Metro",
    "valid_from": "2025-10-01",
    "valid_to": "9999-12-31",
    "parsed_time": "2026-02-01 20:00:45"
  }
]
```

## Supported Date Formats

The scraper can parse various German date formats:

| Format | Example | Result |
|--------|---------|--------|
| Full range | `02.02.2026 - 07.02.2026` | `2026-02-02` to `2026-02-07` |
| Short range | `02.02. - 07.02.2026` | `2026-02-02` to `2026-02-07` |
| Cross-year | `28.12. - 03.01.2026` | `2025-12-28` to `2026-01-03` |
| Open-ended | `von Mittwoch 01.10.2025` | `2025-10-01` to `9999-12-31` |

## Requirements

- Python 3.7+
- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0
- lxml >= 4.9.0
