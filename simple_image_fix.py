#!/usr/bin/env python3
"""
Simple fix for image extraction - directly updates the broken method
"""

def fix_image_extraction():
    """Fix the image extraction method in wilo_scraper.py"""
    
    print("Fixing image extraction in wilo_scraper.py...")
    
    # Read current file
    with open('scraper/wilo_scraper.py', 'r') as f:
        lines = f.readlines()
    
    # Find the problematic method and replace it entirely
    new_lines = []
    skip_lines = False
    method_found = False
    
    for i, line in enumerate(lines):
        # Find the start of the problematic method
        if 'def _extract_products_from_current_view(self, category, subcategory):' in line:
            method_found = True
            skip_lines = True
            # Add the fixed method
            new_lines.extend([
                '    def _extract_products_from_current_view(self, category, subcategory):\n',
                '        """Extract products from current page view with WORKING image extraction"""\n',
                '        try:\n',
                '            driver = self.browser_manager.get_driver()\n',
                '            products = []\n',
                '            \n',
                '            self.browser_manager.take_screenshot(f"step8_products_{subcategory[:10]}.png")\n',
                '            \n',
                '            # Look for product grid rows\n',
                '            grid_row_selectors = [\n',
                '                "//tr[contains(@class, \'jqgrow\')]",\n',
                '                "//tr[contains(@class, \'ui-widget-content\')]",\n',
                '                "//tbody//tr[@role=\'row\']"\n',
                '            ]\n',
                '            \n',
                '            for selector in grid_row_selectors:\n',
                '                try:\n',
                '                    rows = driver.find_elements(By.XPATH, selector)\n',
                '                    self.logger.info(f"Found {len(rows)} grid rows with selector: {selector}")\n',
                '                    \n',
                '                    for i, row in enumerate(rows):\n',
                '                        try:\n',
                '                            # Extract product name\n',
                '                            name_element = row.find_element(By.XPATH, ".//span[@class=\'common_lbl_bold\']")\n',
                '                            product_name = name_element.text.strip()\n',
                '                            \n',
                '                            if not product_name or len(product_name) < 3:\n',
                '                                continue\n',
                '                            \n',
                '                            # WORKING IMAGE EXTRACTION\n',
                '                            image_url = ""\n',
                '                            has_image = False\n',
                '                            \n',
                '                            try:\n',
                '                                # Find div with background-image style\n',
                '                                img_div = row.find_element(By.XPATH, ".//div[contains(@style, \'background-image\')]")\n',
                '                                style_attr = img_div.get_attribute(\'style\')\n',
                '                                \n',
                '                                if \'background-image:\' in style_attr and \'url(\' in style_attr:\n',
                '                                    # Extract URL from background-image with proper HTML entity handling\n',
                '                                    if \'url(&quot;\' in style_attr:\n',
                '                                        # Handle HTML entity encoded URLs\n',
                '                                        start_pos = style_attr.find(\'url(&quot;\') + len(\'url(&quot;\')\n',
                '                                        end_pos = style_attr.find(\'&quot;)\', start_pos)\n',
                '                                        \n',
                '                                        if end_pos > start_pos:\n',
                '                                            encoded_url = style_attr[start_pos:end_pos]\n',
                '                                            # Decode HTML entities\n',
                '                                            decoded_url = encoded_url.replace(\'&amp;\', \'&\').replace(\'&quot;\', \'"\')\n',
                '                                            \n',
                '                                            # Build complete URL\n',
                '                                            if decoded_url.startswith(\'ApplRangeHandler\'):\n',
                '                                                image_url = f"https://select.wilo.com/{decoded_url}"\n',
                '                                            else:\n',
                '                                                image_url = decoded_url\n',
                '                                            \n',
                '                                            has_image = True\n',
                '                                            self.logger.info(f"Found image via background-image: {image_url}")\n',
                '                                    else:\n',
                '                                        # Handle regular URL format\n',
                '                                        start_pos = style_attr.find(\'url("\') + 5\n',
                '                                        end_pos = style_attr.find(\'")\', start_pos)\n',
                '                                        if end_pos > start_pos:\n',
                '                                            image_url = style_attr[start_pos:end_pos]\n',
                '                                            if image_url.startswith(\'ApplRangeHandler\'):\n',
                '                                                image_url = f"https://select.wilo.com/{image_url}"\n',
                '                                            has_image = True\n',
                '                                            self.logger.info(f"Found image via regular URL: {image_url}")\n',
                '                                            \n',
                '                            except Exception as img_error:\n',
                '                                self.logger.debug(f"Image extraction failed for {product_name}: {img_error}")\n',
                '                            \n',
                '                            # Create product object\n',
                '                            product = {\n',
                '                                \'id\': f"{category.replace(\'.\', \'\').replace(\' \', \'_\')}_{subcategory.replace(\' \', \'_\')}_{i+1}",\n',
                '                                \'name\': product_name,\n',
                '                                \'category\': category,\n',
                '                                \'subcategory\': subcategory,\n',
                '                                \'image_url\': image_url,\n',
                '                                \'has_image\': has_image,\n',
                '                                \'description\': f"Wilo {product_name} - Professional pump for {subcategory} applications in {category}",\n',
                '                                \'specifications\': {\n',
                '                                    \'brand\': \'Wilo\',\n',
                '                                    \'series\': product_name,\n',
                '                                    \'application\': subcategory,\n',
                '                                    \'category\': category,\n',
                '                                    \'type\': \'Pump\'\n',
                '                                },\n',
                '                                \'price\': \'Price on request\',\n',
                '                                \'currency\': \'EUR\',\n',
                '                                \'country\': \'Germany\',\n',
                '                                \'status\': \'Enhanced Real Product - Extracted\',\n',
                '                                \'extracted_at\': time.strftime(\'%Y-%m-%d %H:%M:%S\'),\n',
                '                                \'source_url\': driver.current_url\n',
                '                            }\n',
                '                            \n',
                '                            products.append(product)\n',
                '                            \n',
                '                            if has_image:\n',
                '                                self.logger.info(f"Enhanced extraction - Product: {product_name} [WITH IMAGE]")\n',
                '                            else:\n',
                '                                self.logger.info(f"Enhanced extraction - Product: {product_name} [NO IMAGE]")\n',
                '                            \n',
                '                        except Exception as row_error:\n',
                '                            self.logger.error(f"Error processing row: {row_error}")\n',
                '                            continue\n',
                '                    \n',
                '                    if products:\n',
                '                        break\n',
                '                        \n',
                '                except Exception as selector_error:\n',
                '                    self.logger.error(f"Error with selector {selector}: {selector_error}")\n',
                '                    continue\n',
                '            \n',
                '            # Take screenshot and log summary\n',
                '            if products:\n',
                '                self.browser_manager.take_screenshot(f"step9_extracted_products_{subcategory[:10]}.png")\n',
                '                \n',
                '                with_images = sum(1 for p in products if p[\'has_image\'])\n',
                '                without_images = len(products) - with_images\n',
                '                self.logger.info(f"EXTRACTION SUMMARY for {subcategory}:")\n',
                '                self.logger.info(f"   Total products: {len(products)}")\n',
                '                self.logger.info(f"   With images: {with_images}")\n',
                '                self.logger.info(f"   Without images: {without_images}")\n',
                '            \n',
                '            return products\n',
                '            \n',
                '        except Exception as e:\n',
                '            self.logger.error(f"Failed to extract products from current view: {e}")\n',
                '            return []\n',
                '\n'
            ])
            continue
        
        # Skip lines until we find the next method
        if skip_lines:
            if line.strip().startswith('def ') and not line.strip().startswith('def _extract_products_from_current_view'):
                skip_lines = False
                new_lines.append(line)
            # Skip this line (part of the old method)
            continue
        
        # Keep this line
        new_lines.append(line)
    
    if not method_found:
        print("ERROR: Could not find the method to replace!")
        return False
    
    # Write the fixed file
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Fixed image extraction method!")
    return True

def create_sprite_processor():
    """Create a simple sprite image processor"""
    
    sprite_processor_content = '''"""
Simple sprite image processor for Wilo product images
"""

import requests
from PIL import Image
from io import BytesIO
import os
from pathlib import Path
import re
from utils.logger import get_logger

class SpriteImageProcessor:
    """Simple processor for Wilo sprite sheets"""
    
    def __init__(self, output_dir="images/products"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
        self.sprite_cache = {}
        
    def process_product_image(self, product_data):
        """Process a product image from sprite sheet"""
        try:
            sprite_url = product_data.get('image_url', '')
            if not sprite_url or not product_data.get('has_image', False):
                return None
            
            # Download sprite sheet
            sprite_image = self._download_sprite(sprite_url)
            if not sprite_image:
                return None
            
            # For now, save the first 64x64 portion (top-left)
            # Later you can enhance this to use actual background-position
            cropped = sprite_image.crop((0, 0, 64, 64))
            
            # Save individual image
            return self._save_product_image(cropped, product_data)
            
        except Exception as e:
            self.logger.error(f"Failed to process image for {product_data.get('name', 'Unknown')}: {e}")
            return None
    
    def _download_sprite(self, url):
        """Download sprite sheet"""
        try:
            if url in self.sprite_cache:
                return self.sprite_cache[url]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            sprite = Image.open(BytesIO(response.content))
            self.sprite_cache[url] = sprite
            
            self.logger.info(f"Downloaded sprite: {sprite.size}")
            return sprite
            
        except Exception as e:
            self.logger.error(f"Failed to download sprite: {e}")
            return None
    
    def _save_product_image(self, image, product_data):
        """Save individual product image"""
        try:
            name = product_data.get('name', 'unknown')
            category = product_data.get('category', '').replace('.', '').replace(' ', '_')
            
            # Clean filename
            safe_name = re.sub(r'[<>:"/\\\\|?*]', '_', name)
            filename = f"{category}_{safe_name}.png"
            
            filepath = self.output_dir / filename
            image.save(filepath, 'PNG')
            
            self.logger.info(f"Saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save image: {e}")
            return None
'''
    
    # Write the sprite processor
    utils_dir = Path('utils')
    utils_dir.mkdir(exist_ok=True)
    
    with open('utils/sprite_processor.py', 'w') as f:
        f.write(sprite_processor_content)
    
    print("✅ Created sprite processor!")

def main():
    """Main function"""
    print("🖼️ Fixing Image Extraction for Wilo Scraper")
    print("=" * 50)
    
    # Fix the main scraper file
    if fix_image_extraction():
        print("✅ Image extraction method fixed!")
    else:
        print("❌ Failed to fix image extraction")
        return
    
    # Create sprite processor
    create_sprite_processor()
    
    print("\n" + "=" * 50)
    print("✅ ALL FIXES APPLIED!")
    print("=" * 50)
    
    print("\nWhat was fixed:")
    print("• Fixed the broken _extract_products_from_current_view method")
    print("• Proper HTML entity decoding (&amp; → &, &quot; → \")")
    print("• Enhanced image URL extraction")
    print("• Added has_image flag to products")
    print("• Created simple sprite processor utility")
    
    print("\nNext steps:")
    print("1. Install Pillow: pip install Pillow")
    print("2. Run your scraper: python main.py")
    print("3. Check that images are being extracted")
    print("4. Use utils/sprite_processor.py for individual images if needed")
    
    print("\n🚀 Your scraper should now work without errors!")

if __name__ == "__main__":
    main()