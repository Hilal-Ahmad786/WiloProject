#!/usr/bin/env python3
"""
Script to create all module files for the Wilo scraper project
Run this script to generate the complete modular structure
"""

import os
from pathlib import Path

def create_directories():
    """Create all necessary directories"""
    directories = [
        "config",
        "gui",
        "gui/widgets",
        "gui/dialogs",
        "scraper",
        "scraper/navigation",
        "scraper/extractors",
        "shopify",
        "utils",
        "data",
        "logs",
        "logs/screenshots"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files for Python packages
        if not directory.startswith(('data', 'logs')):
            init_file = Path(directory) / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Module package"""\n')
    
    print("✅ Created directory structure")

def create_navigation_modules():
    """Create navigation modules"""
    
    # Country selector navigation
    country_nav_content = '''"""
Country selection navigation logic
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import time

class CountryNavigator:
    """Handles country selection navigation"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def select_country(self, driver, country: str) -> bool:
        """Select a country from the list"""
        try:
            self.logger.info(f"Selecting country: {country}")
            wait = WebDriverWait(driver, 20)
            
            # Strategy 1: Find button by value attribute
            try:
                country_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[@value='{country}']"))
                )
                driver.execute_script("arguments[0].click();", country_button)
                self.logger.info("Country selected via button value")
                time.sleep(self.settings.scraping.delay_between_actions)
                return True
            except:
                pass
            
            # Strategy 2: Find button by text content  
            try:
                country_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(.//span, '{country}')]"))
                )
                driver.execute_script("arguments[0].click();", country_button)
                self.logger.info("Country selected via button text")
                time.sleep(self.settings.scraping.delay_between_actions)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to select country {country}: {e}")
            return False
'''
    
    # Pump selector navigation
    pump_nav_content = '''"""
Pump selection navigation logic
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import time

class PumpNavigator:
    """Handles pump selection navigation"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def navigate_to_pump_selection(self, driver) -> bool:
        """Navigate to hydraulic pump selection"""
        try:
            self.logger.info("Navigating to pump selection...")
            wait = WebDriverWait(driver, 20)
            
            # Find the tile with "Hydraulische Pumpenauswahl"
            try:
                pump_element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//span[contains(text(), 'Hydraulische Pumpenauswahl')]//ancestor::div[contains(@class, 'tileButton')]"
                    ))
                )
                
                driver.execute_script("arguments[0].scrollIntoView(true);", pump_element)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", pump_element)
                
                self.logger.info("Pump selection successful")
                time.sleep(self.settings.scraping.delay_between_actions)
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to find pump selection tile: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to navigate to pump selection: {e}")
            return False
'''
    
    # Category handler
    category_handler_content = '''"""
Category handling logic
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from typing import List, Dict
import time

class CategoryHandler:
    """Handles category detection and selection"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def get_categories(self, driver) -> List[Dict]:
        """Get available categories"""
        try:
            categories = []
            
            # Try dropdown approach
            try:
                category_elements = driver.find_elements(By.XPATH, "//ul[@class='rcbList']//li")
                for elem in category_elements:
                    text = elem.text.strip()
                    if text:
                        categories.append({
                            'name': text,
                            'element': elem,
                            'type': 'dropdown'
                        })
            except:
                pass
            
            # Try tree approach if dropdown failed
            if not categories:
                try:
                    tree_items = driver.find_elements(By.XPATH, "//ul[@class='jstree-children']//a")
                    for elem in tree_items:
                        text = elem.text.strip()
                        if text:
                            categories.append({
                                'name': text,
                                'element': elem,
                                'type': 'tree'
                            })
                except:
                    pass
            
            self.logger.info(f"Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            return []
    
    def select_category(self, driver, category: Dict) -> bool:
        """Select a specific category"""
        try:
            element = category['element']
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", element)
            
            time.sleep(self.settings.scraping.delay_between_actions)
            self.logger.info(f"Selected category: {category['name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select category {category['name']}: {e}")
            return False
'''
    
    # Write files
    Path("scraper/navigation/country_selector.py").write_text(country_nav_content)
    Path("scraper/navigation/pump_selector.py").write_text(pump_nav_content)
    Path("scraper/navigation/category_handler.py").write_text(category_handler_content)
    
    print("✅ Created navigation modules")

def create_extractor_modules():
    """Create data extraction modules"""
    
    product_extractor_content = '''"""
Product data extraction logic
"""

from selenium.webdriver.common.by import By
from utils.logger import get_logger
from datetime import datetime
from typing import Dict, Optional

class ProductExtractor:
    """Extracts product data from product pages"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def extract_product_data(self, driver, category: str, country: str) -> Optional[Dict]:
        """Extract product data from current page"""
        try:
            data = {
                'category': category,
                'country': country,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract product name
            try:
                name_selectors = [
                    "//h1", "//h2", "//*[@class='product-title']",
                    "//*[contains(@class, 'title')]", "//*[contains(@class, 'name')]"
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = driver.find_element(By.XPATH, selector)
                        if name_element.text.strip():
                            data['name'] = name_element.text.strip()
                            break
                    except:
                        continue
                
                if 'name' not in data:
                    data['name'] = "Unknown Product"
                    
            except Exception as e:
                data['name'] = "Unknown Product"
                self.logger.warning(f"Failed to extract product name: {e}")
            
            # Extract specifications
            specs = {}
            try:
                spec_elements = driver.find_elements(By.XPATH, "//table//tr")
                for row in spec_elements:
                    try:
                        cells = row.find_elements(By.XPATH, ".//td")
                        if len(cells) >= 2:
                            key = cells[0].text.strip()
                            value = cells[1].text.strip()
                            if key and value:
                                specs[key] = value
                    except:
                        continue
            except:
                pass
            
            data['specifications'] = specs
            
            # Extract price
            try:
                price_selectors = [
                    "//*[contains(@class, 'price')]",
                    "//*[contains(text(), '€')]",
                    "//*[contains(text(), '$')]"
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = driver.find_element(By.XPATH, selector)
                        if price_element.text.strip():
                            data['price'] = price_element.text.strip()
                            break
                    except:
                        continue
                
                if 'price' not in data:
                    data['price'] = "Price not available"
                    
            except:
                data['price'] = "Price not available"
            
            # Extract description
            try:
                desc_selectors = [
                    "//div[@class='description']",
                    "//*[contains(@class, 'desc')]",
                    "//p[contains(@class, 'description')]"
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_element = driver.find_element(By.XPATH, selector)
                        if desc_element.text.strip():
                            data['description'] = desc_element.text.strip()
                            break
                    except:
                        continue
                
                if 'description' not in data:
                    data['description'] = ""
                    
            except:
                data['description'] = ""
            
            # Extract images
            if self.settings.scraping.download_images:
                try:
                    img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'product')]")
                    data['images'] = [
                        img.get_attribute('src') 
                        for img in img_elements 
                        if img.get_attribute('src')
                    ]
                except:
                    data['images'] = []
            else:
                data['images'] = []
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to extract product data: {e}")
            return None
'''
    
    Path("scraper/extractors/product_extractor.py").write_text(product_extractor_content)
    print("✅ Created extractor modules")

def create_utility_modules():
    """Create utility modules"""
    
    screenshot_manager_content = '''"""
Screenshot management utilities
"""

import os
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

class ScreenshotManager:
    """Manages debug screenshots"""
    
    def __init__(self, screenshots_dir: str = "logs/screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
    
    def take_screenshot(self, driver, name: str) -> str:
        """Take a screenshot with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            driver.save_screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def cleanup_old_screenshots(self, days: int = 7):
        """Remove screenshots older than specified days"""
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            removed_count = 0
            for screenshot in self.screenshots_dir.glob("*.png"):
                if screenshot.stat().st_mtime < cutoff_time:
                    screenshot.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} old screenshots")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup screenshots: {e}")
'''
    
    file_manager_content = '''"""
File management utilities
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import get_logger

class FileManager:
    """Handles file operations for scraped data"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def export_to_json(self, data: List[Dict], filepath: str) -> bool:
        """Export data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data exported to JSON: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            return False
    
    def export_to_csv(self, data: List[Dict], filepath: str) -> bool:
        """Export data to CSV file"""
        try:
            if not data:
                return False
            
            fieldnames = ['name', 'category', 'price', 'description', 'country']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in data:
                    row = {
                        'name': product.get('name', ''),
                        'category': product.get('category', ''),
                        'price': product.get('price', ''),
                        'description': product.get('description', ''),
                        'country': product.get('country', '')
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Data exported to CSV: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            return False
    
    def load_from_json(self, filepath: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Data loaded from JSON: {filepath}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON: {e}")
            return []
'''
    
    Path("utils/screenshot_manager.py").write_text(screenshot_manager_content)
    Path("utils/file_manager.py").write_text(file_manager_content)
    print("✅ Created utility modules")

def create_widget_modules():
    """Create remaining widget modules"""
    
    browser_settings_content = '''"""
Browser settings widget
"""

import tkinter as tk
from tkinter import ttk

class BrowserSettings(ttk.LabelFrame):
    """Widget for browser configuration"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Browser Settings", padding="10")
        
        self.settings = settings
        self._create_widgets()
    
    def _create_widgets(self):
        """Create browser setting widgets"""
        self.headless_var = tk.BooleanVar(value=self.settings.scraping.headless_mode)
        ttk.Checkbutton(
            self, 
            text="Run in headless mode", 
            variable=self.headless_var
        ).pack(anchor='w')
        
        delay_frame = ttk.Frame(self)
        delay_frame.pack(fill='x', pady=5)
        
        ttk.Label(delay_frame, text="Delay between actions (seconds):").pack(side='left')
        self.delay_var = tk.StringVar(value=str(self.settings.scraping.delay_between_actions))
        ttk.Entry(delay_frame, textvariable=self.delay_var, width=10).pack(side='left', padx=5)
    
    def update_settings(self):
        """Update settings from widget values"""
        self.settings.scraping.headless_mode = self.headless_var.get()
        
        try:
            self.settings.scraping.delay_between_actions = int(self.delay_var.get())
        except ValueError:
            pass
'''
    
    shopify_config_content = '''"""
Shopify configuration widget
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests

class ShopifyConfig(ttk.LabelFrame):
    """Widget for Shopify configuration"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Shopify Configuration", padding="10")
        
        self.settings = settings
        self._create_widgets()
    
    def _create_widgets(self):
        """Create Shopify config widgets"""
        # Shop URL
        ttk.Label(self, text="Shop URL:").grid(row=0, column=0, sticky='w', pady=2)
        self.shop_url_var = tk.StringVar(value=self.settings.shopify.shop_url)
        ttk.Entry(self, textvariable=self.shop_url_var, width=50).grid(row=0, column=1, pady=2)
        
        # Access Token
        ttk.Label(self, text="Access Token:").grid(row=1, column=0, sticky='w', pady=2)
        self.access_token_var = tk.StringVar(value=self.settings.shopify.access_token)
        ttk.Entry(self, textvariable=self.access_token_var, width=50, show="*").grid(row=1, column=1, pady=2)
        
        # Buttons
        ttk.Button(self, text="Test Connection", command=self.test_connection).grid(row=2, column=0, pady=10)
        ttk.Button(self, text="Upload to Shopify", command=self.upload_to_shopify).grid(row=2, column=1, pady=10)
    
    def test_connection(self):
        """Test Shopify API connection"""
        shop_url = self.shop_url_var.get().strip()
        access_token = self.access_token_var.get().strip()
        
        if not shop_url or not access_token:
            messagebox.showwarning("Missing Info", "Please enter both shop URL and access token.")
            return
        
        try:
            # Fix URL format
            if not shop_url.startswith('http'):
                if not shop_url.endswith('.myshopify.com'):
                    shop_url = f"{shop_url}.myshopify.com"
                shop_url = f"https://{shop_url}"
            
            headers = {
                'X-Shopify-Access-Token': access_token,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{shop_url}/admin/api/2024-01/shop.json", headers=headers, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json().get('shop', {})
                shop_name = shop_data.get('name', 'Unknown')
                messagebox.showinfo("Success", f"✅ Connected to {shop_name}")
            else:
                messagebox.showerror("Error", f"❌ Connection failed: HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Connection error: {str(e)}")
    
    def upload_to_shopify(self):
        """Upload scraped products to Shopify"""
        messagebox.showinfo("Upload", "Shopify upload functionality would be implemented here")
    
    def update_settings(self):
        """Update settings from widget values"""
        self.settings.shopify.shop_url = self.shop_url_var.get().strip()
        self.settings.shopify.access_token = self.access_token_var.get().strip()
'''
    
    results_table_content = '''"""
Results table widget for displaying scraped products
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict

class ResultsTable(ttk.LabelFrame):
    """Widget for displaying scraped products"""
    
    def __init__(self, parent):
        super().__init__(parent, text="Scraping Results", padding="10")
        
        self.total_products = 0
        self._create_widgets()
    
    def _create_widgets(self):
        """Create results table widgets"""
        # Summary
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill='x', pady=5)
        
        ttk.Label(summary_frame, text="Total Products:").pack(side='left')
        self.total_label = ttk.Label(summary_frame, text="0", font=('Arial', 12, 'bold'))
        self.total_label.pack(side='left', padx=10)
        
        # Table
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('Name', 'Category', 'Price', 'Country')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def add_product(self, product_data: Dict):
        """Add a product to the table"""
        self.tree.insert('', 'end', values=(
            product_data.get('name', 'Unknown'),
            product_data.get('category', 'Unknown'),
            product_data.get('price', 'N/A'),
            product_data.get('country', 'Unknown')
        ))
        
        self.total_products += 1
        self.total_label.config(text=str(self.total_products))
    
    def clear(self):
        """Clear all products from table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.total_products = 0
        self.total_label.config(text="0")
'''
    
    Path("gui/widgets/browser_settings.py").write_text(browser_settings_content)
    Path("gui/widgets/shopify_config.py").write_text(shopify_config_content)
    Path("gui/widgets/results_table.py").write_text(results_table_content)
    print("✅ Created widget modules")

def create_init_files():
    """Create __init__.py files for all packages"""
    init_content = '''"""Package initialization"""
'''
    
    packages = [
        "config/__init__.py",
        "gui/__init__.py", 
        "gui/widgets/__init__.py",
        "gui/dialogs/__init__.py",
        "scraper/__init__.py",
        "scraper/navigation/__init__.py", 
        "scraper/extractors/__init__.py",
        "shopify/__init__.py",
        "utils/__init__.py"
    ]
    
    for package in packages:
        if not Path(package).exists():
            Path(package).write_text(init_content)
    
    print("✅ Created __init__.py files")

def create_requirements_file():
    """Create requirements.txt file"""
    requirements_content = """# Core Dependencies
selenium>=4.15.0
requests>=2.31.0
beautifulsoup4>=4.12.2
pandas>=2.1.3
pillow>=10.1.0
python-dotenv>=1.0.0
webdriver-manager>=4.0.0

# Optional Dependencies
aiohttp>=3.8.0
fuzzywuzzy>=0.18.0
python-levenshtein>=0.20.0
schedule>=1.2.0
click>=8.1.0

# Development Dependencies (optional)
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
"""
    
    Path("requirements.txt").write_text(requirements_content)
    print("✅ Created requirements.txt")

def create_readme():
    """Create README.md file"""
    readme_content = """# Wilo Product Scraper

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
"""
    
    Path("README.md").write_text(readme_content)
    print("✅ Created README.md")

def main():
    """Main setup function"""
    print("🚀 Creating Wilo Scraper Modular Structure")
    print("=" * 50)
    
    try:
        create_directories()
        create_navigation_modules()
        create_extractor_modules()
        create_utility_modules()
        create_widget_modules()
        create_init_files()
        create_requirements_file()
        create_readme()
        
        print("\n" + "=" * 50)
        print("✅ MODULAR STRUCTURE CREATED SUCCESSFULLY!")
        print("=" * 50)
        
        print(f"""
📁 Project Structure Created:
   ├── main.py (entry point)
   ├── config/ (settings & countries)
   ├── gui/ (widgets & dialogs)
   ├── scraper/ (navigation & extraction)
   ├── shopify/ (API integration)
   ├── utils/ (logging & utilities)
   └── data/ (storage & exports)

🚀 Next Steps:
1. Copy the module files from previous artifacts
2. Run: pip install -r requirements.txt
3. Configure your settings in config/config.json
4. Run: python main.py

📝 Benefits of This Structure:
- Easy to maintain individual modules
- Update only specific components
- Clear separation of concerns
- Reusable components
- Better testing capabilities
""")
        
    except Exception as e:
        print(f"❌ Error creating structure: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())