#!/usr/bin/env python3
"""
Fixed Enhanced image extraction that handles Wilo's sprite sheet approach
"""

def update_image_extraction():
    """Update the scraper to handle sprite sheet images properly"""
    
    # Read the current scraper file
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # Enhanced image extraction method that handles sprite sheets
    enhanced_image_extraction = '''    def _extract_products_from_current_view(self, category, subcategory):
        """Extract products from current page view with ENHANCED SPRITE SHEET support"""
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
                            
                            # ENHANCED SPRITE SHEET IMAGE EXTRACTION
                            image_info = self._extract_sprite_image_info(row, i)
                            
                            # Enhanced product object with sprite sheet support
                            product = {
                                'id': f"{category.replace('.', '').replace(' ', '_')}_{subcategory.replace(' ', '_')}_{i+1}",
                                'name': product_name,
                                'category': category,
                                'subcategory': subcategory,
                                'image_url': image_info['image_url'],
                                'sprite_sheet_url': image_info['sprite_sheet_url'],
                                'sprite_position': image_info['sprite_position'],
                                'image_dimensions': image_info['dimensions'],
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
                                'source_url': driver.current_url,
                                'has_image': bool(image_info['image_url'] or image_info['sprite_sheet_url'])
                            }
                            
                            products.append(product)
                            
                            if image_info['sprite_sheet_url']:
                                self.logger.info(f"✅ SPRITE IMAGE found for {product_name}: Position {image_info['sprite_position']}")
                            elif image_info['image_url']:
                                self.logger.info(f"✅ DIRECT IMAGE found for {product_name}: {image_info['image_url']}")
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
            
            # Debug: Take screenshot and log summary
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

    def _extract_sprite_image_info(self, row, product_index):
        """Extract sprite sheet image information from product row"""
        try:
            driver = self.browser_manager.get_driver()
            
            image_info = {
                'image_url': '',
                'sprite_sheet_url': '',
                'sprite_position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64}
            }
            
            # Strategy 1: Look for div with background-image style (your case)
            try:
                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                style_attr = img_div.get_attribute('style')
                
                if 'url(' in style_attr:
                    # Extract URL from style
                    start = style_attr.find('url("') + 5
                    if start == 4:  # Try without quotes
                        start = style_attr.find('url(') + 4
                        end = style_attr.find(')', start)
                    else:
                        end = style_attr.find('")', start)
                    
                    if start > 4 and end > start:
                        relative_url = style_attr[start:end]
                        
                        # Decode HTML entities
                        relative_url = relative_url.replace('&quot;', '"').replace('&amp;', '&')
                        
                        # Build full URL
                        if relative_url.startswith('ApplRangeHandler'):
                            sprite_sheet_url = f"https://select.wilo.com/{relative_url}"
                        elif relative_url.startswith('http'):
                            sprite_sheet_url = relative_url
                        else:
                            sprite_sheet_url = f"https://select.wilo.com/{relative_url}"
                        
                        image_info['sprite_sheet_url'] = sprite_sheet_url
                        
                        # Extract background-position for sprite coordinates
                        position_info = self._extract_background_position(style_attr)
                        image_info['sprite_position'] = position_info
                        
                        # Extract dimensions
                        dimensions = self._extract_element_dimensions(img_div)
                        image_info['dimensions'] = dimensions
                        
                        self.logger.debug(f"Sprite sheet URL: {sprite_sheet_url}")
                        self.logger.debug(f"Position: {position_info}")
                        self.logger.debug(f"Dimensions: {dimensions}")
                        
                        # For now, we'll use the sprite sheet URL as the image URL
                        # In a production system, you'd want to crop the individual image
                        image_info['image_url'] = sprite_sheet_url
                        
            except Exception as e:
                self.logger.debug(f"Background-image extraction failed: {e}")
            
            # Strategy 2: Look for direct img elements (fallback)
            if not image_info['sprite_sheet_url']:
                try:
                    img_element = row.find_element(By.XPATH, ".//img[@src]")
                    src = img_element.get_attribute('src')
                    if src:
                        image_info['image_url'] = src if src.startswith('http') else f"https://select.wilo.com/{src}"
                        self.logger.debug(f"Found direct image: {image_info['image_url']}")
                except Exception as e:
                    self.logger.debug(f"Direct image extraction failed: {e}")
            
            return image_info
            
        except Exception as e:
            self.logger.error(f"Failed to extract sprite image info: {e}")
            return {
                'image_url': '',
                'sprite_sheet_url': '',
                'sprite_position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64}
            }
    
    def _extract_background_position(self, style_attr):
        """Extract background-position from CSS style"""
        try:
            import re
            
            # Look for background-position property - Fixed regex pattern
            position_match = re.search(r'background-position:\\s*([^;]+)', style_attr)
            if position_match:
                position_value = position_match.group(1).strip()
                
                # Parse position (e.g., "0px 0px", "-64px -128px")
                parts = position_value.split()
                if len(parts) >= 2:
                    x_str = parts[0].replace('px', '').replace(',', '')
                    y_str = parts[1].replace('px', '').replace(',', '')
                    
                    try:
                        x = int(float(x_str))
                        y = int(float(y_str))
                        return {'x': abs(x), 'y': abs(y)}  # Use absolute values for sprite coordinates
                    except ValueError:
                        pass
            
            return {'x': 0, 'y': 0}
            
        except Exception as e:
            self.logger.debug(f"Background position extraction failed: {e}")
            return {'x': 0, 'y': 0}
    
    def _extract_element_dimensions(self, element):
        """Extract width and height from element"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Try to get dimensions from style
            style = element.get_attribute('style')
            width = height = 64  # Default
            
            import re
            width_match = re.search(r'width:\\s*(\\d+)px', style)
            height_match = re.search(r'height:\\s*(\\d+)px', style)
            
            if width_match:
                width = int(width_match.group(1))
            if height_match:
                height = int(height_match.group(1))
            
            return {'width': width, 'height': height}
            
        except Exception as e:
            self.logger.debug(f"Dimension extraction failed: {e}")
            return {'width': 64, 'height': 64}'''
    
    # Replace the existing method in the file
    import re
    
    # Find and replace the _extract_products_from_current_view method
    pattern = r'def _extract_products_from_current_view\(self, category, subcategory\):.*?(?=\n    def |\n\nclass |\Z)'
    
    new_content = re.sub(pattern, enhanced_image_extraction, content, flags=re.DOTALL)
    
    # Write the updated content
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Enhanced image extraction with sprite sheet support implemented!")

def main():
    print("🖼️ Implementing Enhanced Image Extraction for Sprite Sheets")
    print("=" * 60)
    
    # Update the main scraper
    update_image_extraction()
    
    print("\n✅ Enhanced image extraction implemented!")
    print("\n🎯 What's new:")
    print("• Properly extracts sprite sheet URLs")
    print("• Decodes HTML entities (&amp;, &quot;)")
    print("• Extracts background-position for sprite coordinates")
    print("• Records image dimensions")
    print("• Stores sprite sheet URL for future processing")
    
    print("\n📋 Current behavior:")
    print("• Your scraper will now extract the sprite sheet URL")
    print("• It records the position within the sprite")
    print("• For Shopify upload, it uses the sprite sheet URL")
    
    print("\n🚀 Try running:")
    print("python main.py")

if __name__ == "__main__":
    main()