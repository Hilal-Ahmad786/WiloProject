# Wilo Product Scraper

A modular web scraper for Wilo pump products with Shopify integration.

## Features

- Multi-country support (30+ European countries)
- GUI dashboard with progress tracking
- Shopify API integration for product upload
- Modular architecture for easy maintenance
- Comprehensive error handling and logging
- Debug navigation testing

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure settings:**
   Edit `config/config.json` or set environment variables:
   ```bash
   export SHOPIFY_SHOP_URL="your-shop.myshopify.com"
   export SHOPIFY_ACCESS_TOKEN="your_token"
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Project Structure

```
wilo-scraper/
├── main.py                     # Application entry point
├── config/                     # Configuration management
├── gui/                        # GUI components
├── scraper/                    # Scraping logic
├── shopify/                    # Shopify integration
├── utils/                      # Utility modules
└── data/                       # Data storage
```

## Usage

1. **Select Country**: Choose target country from dropdown
2. **Configure Browser**: Set headless mode and delays
3. **Test Navigation**: Use "Test Navigation" to debug
4. **Start Scraping**: Begin product scraping
5. **Export Data**: Save results to JSON/CSV
6. **Upload to Shopify**: Sync products with your store

## Configuration

Edit `config/config.json` to customize:

```json
{
  "scraping": {
    "max_products_per_category": 100,
    "delay_between_actions": 2,
    "headless_mode": false
  },
  "shopify": {
    "shop_url": "your-shop.myshopify.com",
    "access_token": "your_token"
  }
}
```

## Modules

- **config/**: Settings and country mappings
- **gui/widgets/**: Reusable UI components
- **scraper/navigation/**: Website navigation logic
- **scraper/extractors/**: Data extraction logic
- **utils/**: Logging, screenshots, file management

## Troubleshooting

1. **Chrome Issues**: Update Chrome and ChromeDriver
2. **Navigation Failures**: Use "Test Navigation" for debugging
3. **Shopify Errors**: Verify API token and permissions
4. **Rate Limiting**: Increase delays in browser settings

## Development

To add new features:

1. **New Countries**: Update `config/countries.py`
2. **New Extractors**: Add to `scraper/extractors/`
3. **New Widgets**: Add to `gui/widgets/`
4. **New Shopify Features**: Extend `shopify/` modules

## License

This project is for educational and commercial use. Respect website terms of service.
# WiloProject
