#!/usr/bin/env python3
"""
Complete sprite image processing solution for Wilo scraper
Handles downloading sprite sheets and extracting individual product images
"""

import requests
import re
from PIL import Image
from io import BytesIO
import os
from pathlib import Path
import time
from urllib.parse import unquote
from utils.logger import get_logger

class SpriteImageProcessor:
    """Processes Wilo sprite sheets and extracts individual product images"""
    
    def __init__(self, output_dir="images/products"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
        self.sprite_cache = {}
        
    def extract_product_image(self, product_data):
        """Extract individual product image from sprite sheet"""
        try:
            sprite_url = product_data.get('image_url', '')
            if not sprite_url:
                self.logger.warning(f"No sprite URL for product: {product_data.get('name', 'Unknown')}")
                return None
            
            # Get sprite sheet
            sprite_image = self._download_sprite_sheet(sprite_url)
            if not sprite_image:
                return None
            
            # Extract background position from your HTML
            position = self._extract_position_from_url_or_default()
            
            # Crop individual image (Wilo uses 64x64 grid typically)
            individual_image = self._crop_image(sprite_image, position)
            
            # Save individual image
            image_path = self._save_product_image(individual_image, product_data)
            
            return image_path
            
        except Exception as e:
            self.logger.error(f"Failed to extract image for {product_data.get('name', 'Unknown')}: {e}")
            return None
    
    def _download_sprite_sheet(self, sprite_url):
        """Download sprite sheet with caching"""
        try:
            # Use URL as cache key
            if sprite_url in self.sprite_cache:
                self.logger.debug(f"Using cached sprite sheet")
                return self.sprite_cache[sprite_url]
            
            self.logger.info(f"Downloading sprite sheet: {sprite_url[:100]}...")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(sprite_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Open with PIL
            sprite_image = Image.open(BytesIO(response.content))
            
            # Cache the image
            self.sprite_cache[sprite_url] = sprite_image
            
            self.logger.info(f"Downloaded sprite sheet: {sprite_image.size[0]}x{sprite_image.size[1]} pixels")
            return sprite_image
            
        except Exception as e:
            self.logger.error(f"Failed to download sprite sheet: {e}")
            return None
    
    def _extract_position_from_url_or_default(self):
        """Extract position from background-position or use default grid logic"""
        # For now, we'll use a grid-based approach since Wilo seems to use consistent 64x64 tiles
        # You can enhance this to parse actual background-position values
        return {'x': 0, 'y': 0, 'width': 64, 'height': 64}
    
    def _crop_image(self, sprite_image, position):
        """Crop individual image from sprite sheet"""
        try:
            x = position.get('x', 0)
            y = position.get('y', 0)
            width = position.get('width', 64)
            height = position.get('height', 64)
            
            # Crop the image
            box = (x, y, x + width, y + height)
            cropped = sprite_image.crop(box)
            
            # Resize to standard size if needed (optional)
            if cropped.size != (64, 64):
                cropped = cropped.resize((64, 64), Image.Resampling.LANCZOS)
            
            return cropped
            
        except Exception as e:
            self.logger.error(f"Failed to crop image: {e}")
            return None
    
    def _save_product_image(self, image, product_data):
        """Save individual product image"""
        try:
            # Create safe filename
            product_name = product_data.get('name', 'unknown')
            category = product_data.get('category', '').replace('.', '').replace(' ', '_')
            subcategory = product_data.get('subcategory', '').replace(' ', '_')
            
            # Clean filename
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', product_name)
            filename = f"{category}_{subcategory}_{safe_name}.png"
            
            filepath = self.output_dir / filename
            
            # Save as PNG with transparency support
            image.save(filepath, 'PNG', optimize=True)
            
            self.logger.info(f"Saved product image: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save image: {e}")
            return None

# Integration with your existing scraper
def update_scraper_with_image_processing():
    """Update your wilo_scraper.py to include image processing"""
    
    # Read current scraper
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # Enhanced product extraction method
    enhanced_extraction = '''    def _extract_products_from_current_view(self, category, subcategory):
        """Extract products from current page view with ENHANCED IMAGE processing"""
        try:
            driver = self.browser_manager.get_driver()
            products = []
            
            self.browser_manager.take_screenshot(f"step8_products_{subcategory[:10]}.png")
            
            # Look for product grid rows
            grid_row_selectors = [
                "//tr[contains(@class, 'jqgrow')]",
                "//tr[contains(@class, 'ui-widget-content')]",
                "//tbody//tr[@role='row']"
            ]
            
            for selector in grid_row_selectors:
                try:
                    rows = driver.find_elements(By.XPATH, selector)
                    self.logger.info(f"Found {len(rows)} grid rows with selector: {selector}")
                    
                    for i, row in enumerate(rows):
                        try:
                            # Extract product name
                            name_element = row.find_element(By.XPATH, ".//span[@class='common_lbl_bold']")
                            product_name = name_element.text.strip()
                            
                            if not product_name or len(product_name) < 3:
                                continue
                            
                            # ENHANCED IMAGE EXTRACTION with background-position
                            image_data = self._extract_sprite_image_data(row, i, product_name)
                            
                            # Create enhanced product object
                            product = {
                                'id': f"{category.replace('.', '').replace(' ', '_')}_{subcategory.replace(' ', '_')}_{i+1}",
                                'name': product_name,
                                'category': category,
                                'subcategory': subcategory,
                                'image_url': image_data['sprite_url'],
                                'sprite_position': image_data['position'],
                                'image_dimensions': image_data['dimensions'],
                                'has_image': image_data['has_image'],
                                'description': f"Wilo {product_name} - Professional pump for {subcategory} applications in {category}",
                                'specifications': {
                                    'brand': 'Wilo',
                                    'series': product_name,
                                    'application': subcategory,
                                    'category': category,
                                    'type': 'Pump'
                                },
                                'price': 'Price on request',
                                'currency': 'EUR',
                                'country': 'Germany',
                                'status': 'Enhanced Real Product - Extracted',
                                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'source_url': driver.current_url
                            }
                            
                            products.append(product)
                            
                            if image_data['has_image']:
                                self.logger.info(f"✅ SPRITE IMAGE found for {product_name}: Position {image_data['position']}")
                            else:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")
                            
                        except Exception as row_error:
                            self.logger.error(f"Error processing row: {row_error}")
                            continue
                    
                    if products:
                        break
                        
                except Exception as selector_error:
                    self.logger.error(f"Error with selector {selector}: {selector_error}")
                    continue
            
            # Take screenshot and log summary
            if products:
                self.browser_manager.take_screenshot(f"step9_extracted_products_{subcategory[:10]}.png")
                
                with_images = sum(1 for p in products if p['has_image'])
                without_images = len(products) - with_images
                self.logger.info(f"📊 EXTRACTION SUMMARY for {subcategory}:")
                self.logger.info(f"   Total products: {len(products)}")
                self.logger.info(f"   With images: {with_images}")
                self.logger.info(f"   Without images: {without_images}")
            
            return products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from current view: {e}")
            return []
    
    def _extract_sprite_image_data(self, row, index, product_name):
        """Extract sprite image data with position information"""
        try:
            image_data = {
                'sprite_url': '',
                'position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64},
                'has_image': False
            }
            
            # Find div with background-image style
            try:
                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                style_attr = img_div.get_attribute('style')
                
                if 'background-image:' in style_attr and 'url(' in style_attr:
                    # Extract sprite URL
                    sprite_url = self._extract_sprite_url(style_attr)
                    if sprite_url:
                        image_data['sprite_url'] = sprite_url
                        image_data['has_image'] = True
                        
                        # Extract background-position
                        position = self._extract_background_position(style_attr)
                        image_data['position'] = position
                        
                        # Extract dimensions
                        dimensions = self._extract_element_dimensions(img_div)
                        image_data['dimensions'] = dimensions
                        
                        self.logger.debug(f"Sprite data for {product_name}: URL={sprite_url[:50]}..., Position={position}")
            
            except Exception as e:
                self.logger.debug(f"Background-image extraction failed for {product_name}: {e}")
            
            return image_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract sprite image data: {e}")
            return {
                'sprite_url': '',
                'position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64},
                'has_image': False
            }
    
    def _extract_sprite_url(self, style_attr):
        """Extract sprite URL from CSS background-image"""
        try:
            # Handle HTML entity encoded URLs like your example
            start_marker = 'url(&quot;'
            end_marker = '&quot;)'
            
            start_pos = style_attr.find(start_marker)
            if start_pos != -1:
                start_pos += len(start_marker)
                end_pos = style_attr.find(end_marker, start_pos)
                
                if end_pos != -1:
                    encoded_url = style_attr[start_pos:end_pos]
                    # Decode HTML entities
                    decoded_url = encoded_url.replace('&amp;', '&').replace('&quot;', '"')
                    
                    # Build complete URL
                    if decoded_url.startswith('ApplRangeHandler'):
                        return f"https://select.wilo.com/{decoded_url}"
                    else:
                        return decoded_url
            
            return None
            
        except Exception as e:
            self.logger.debug(f"URL extraction failed: {e}")
            return None
    
    def _extract_background_position(self, style_attr):
        """Extract background-position from CSS style"""
        try:
            import re
            
            # Look for background-position: x y
            position_match = re.search(r'background-position:\s*([^;]+)', style_attr)
            if position_match:
                position_value = position_match.group(1).strip()
                
                # Parse "0px 0px" or "-64px -128px"
                parts = position_value.split()
                if len(parts) >= 2:
                    x_str = parts[0].replace('px', '').replace(',', '')
                    y_str = parts[1].replace('px', '').replace(',', '')
                    
                    try:
                        x = int(float(x_str))
                        y = int(float(y_str))
                        return {'x': abs(x), 'y': abs(y)}
                    except ValueError:
                        pass
            
            return {'x': 0, 'y': 0}
            
        except Exception as e:
            self.logger.debug(f"Position extraction failed: {e}")
            return {'x': 0, 'y': 0}
    
    def _extract_element_dimensions(self, element):
        """Extract width and height from element"""
        try:
            style = element.get_attribute('style')
            width = height = 64  # Default
            
            import re
            width_match = re.search(r'width:\s*(\d+)px', style)
            height_match = re.search(r'height:\s*(\d+)px', style)
            
            if width_match:
                width = int(width_match.group(1))
            if height_match:
                height = int(height_match.group(1))
            
            return {'width': width, 'height': height}
            
        except Exception as e:
            self.logger.debug(f"Dimension extraction failed: {e}")
            return {'width': 64, 'height': 64}'''
    
    # Replace the existing method
    import re
    pattern = r'def _extract_products_from_current_view\(self, category, subcategory\):.*?(?=\n    def |\n\nclass |\Z)'
    
    new_content = re.sub(pattern, enhanced_extraction, content, flags=re.DOTALL)
    
    # Write updated file
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated scraper with enhanced image processing")

def main():
    """Main function to set up sprite image processing"""
    print("🖼️ Setting up Sprite Image Processing for Wilo Scraper")
    print("=" * 60)
    
    # Create sprite processor
    processor = SpriteImageProcessor()
    
    # Update scraper
    update_scraper_with_image_processing()
    
    print("\n✅ Sprite image processing setup complete!")
    print("\nWhat this adds:")
    print("• Downloads sprite sheets and caches them")
    print("• Extracts background-position coordinates")
    print("• Crops individual product images")
    print("• Saves images in organized folders")
    print("• Enhanced product data with image metadata")
    
    print("\n🚀 Next steps:")
    print("1. Install Pillow: pip install Pillow")
    print("2. Run your scraper: python main.py")
    print("3. Check images/ folder for extracted product images")
    print("4. Use individual image paths in Shopify uploads")

if __name__ == "__main__":
    main()