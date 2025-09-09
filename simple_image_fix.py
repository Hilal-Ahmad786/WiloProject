#!/usr/bin/env python3
"""
Simple approach to fix image extraction - adds new methods without regex replacement
"""

def add_enhanced_image_methods():
    """Add enhanced image extraction methods to the scraper"""
    
    # Read the current scraper file
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # New methods to add at the end of the class (before the last method)
    new_methods = '''
    def _extract_sprite_image_info(self, row, product_index):
        """Extract sprite sheet image information from product row"""
        try:
            image_info = {
                'image_url': '',
                'sprite_sheet_url': '',
                'sprite_position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64}
            }
            
            # Look for div with background-image style
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
                        image_info['image_url'] = sprite_sheet_url  # Use sprite as image for now
                        
                        # Extract background-position
                        position_info = self._extract_background_position(style_attr)
                        image_info['sprite_position'] = position_info
                        
                        # Extract dimensions  
                        dimensions = self._extract_element_dimensions(img_div)
                        image_info['dimensions'] = dimensions
                        
                        self.logger.debug(f"Sprite URL: {sprite_sheet_url}")
                        self.logger.debug(f"Position: {position_info}")
                        
            except Exception as e:
                self.logger.debug(f"Background-image extraction failed: {e}")
            
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
            # Simple string search for background-position
            if 'background-position:' in style_attr:
                start_idx = style_attr.find('background-position:') + len('background-position:')
                end_idx = style_attr.find(';', start_idx)
                if end_idx == -1:
                    end_idx = len(style_attr)
                
                position_value = style_attr[start_idx:end_idx].strip()
                
                # Parse position (e.g., "0px 0px", "-64px -128px")
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
            self.logger.debug(f"Background position extraction failed: {e}")
            return {'x': 0, 'y': 0}
    
    def _extract_element_dimensions(self, element):
        """Extract width and height from element"""
        try:
            style = element.get_attribute('style')
            width = height = 64  # Default
            
            # Simple string parsing for dimensions
            if 'width:' in style:
                start_idx = style.find('width:') + len('width:')
                end_idx = style.find('px', start_idx)
                if end_idx > start_idx:
                    try:
                        width = int(style[start_idx:end_idx].strip())
                    except ValueError:
                        pass
            
            if 'height:' in style:
                start_idx = style.find('height:') + len('height:')
                end_idx = style.find('px', start_idx)
                if end_idx > start_idx:
                    try:
                        height = int(style[start_idx:end_idx].strip())
                    except ValueError:
                        pass
            
            return {'width': width, 'height': height}
            
        except Exception as e:
            self.logger.debug(f"Dimension extraction failed: {e}")
            return {'width': 64, 'height': 64}
'''
    
    # Find where to insert the new methods (before the last method)
    # Look for the last method definition
    last_method_pos = content.rfind('    def ')
    if last_method_pos != -1:
        # Find the end of the previous method (before the last one)
        prev_method_end = content.rfind('\n    def ', 0, last_method_pos)
        if prev_method_end != -1:
            # Find the actual insertion point (end of previous method)
            insertion_point = content.find('\n    def ', prev_method_end + 1)
            if insertion_point != -1:
                # Insert the new methods before the last method
                new_content = content[:insertion_point] + new_methods + '\n' + content[insertion_point:]
            else:
                # Fallback: add at the end of the class
                new_content = content.replace('    def stop(self):', new_methods + '\n    def stop(self):')
        else:
            # Fallback: add at the end of the class
            new_content = content.replace('    def stop(self):', new_methods + '\n    def stop(self):')
    else:
        # Fallback: add at the end of the file
        new_content = content + new_methods
    
    # Write the updated content
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added enhanced image extraction methods!")

def update_existing_method():
    """Update the existing _extract_products_from_current_view method"""
    
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # Look for the specific line where image extraction happens
    old_line = "# ENHANCED IMAGE EXTRACTION - Multiple strategies"
    new_line = "# ENHANCED SPRITE SHEET IMAGE EXTRACTION"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
    
    # Replace the image extraction block
    old_block = '''# Extract image URL from background-image style
                            image_url = ""
                            try:
                                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                                style_attr = img_div.get_attribute('style')
                                if 'url(' in style_attr:
                                    start = style_attr.find('url("') + 5
                                    end = style_attr.find('")', start)
                                    if start > 4 and end > start:
                                        relative_url = style_attr[start:end]
                                        # Convert to absolute URL
                                        if relative_url.startswith('ApplRangeHandler'):
                                            image_url = f"https://select.wilo.com/{relative_url}"
                                        else:
                                            image_url = relative_url
                            except:
                                pass'''
    
    new_block = '''# ENHANCED SPRITE SHEET IMAGE EXTRACTION
                            image_info = self._extract_sprite_image_info(row, i)
                            image_url = image_info['image_url']'''
    
    if old_block in content:
        content = content.replace(old_block, new_block)
        print("✅ Updated existing image extraction logic!")
    else:
        print("⚠️ Could not find exact block to replace, but new methods added.")
    
    # Add sprite info to product object
    old_product_line = "'image_url': image_url,"
    new_product_lines = """'image_url': image_info['image_url'],
                                'sprite_sheet_url': image_info['sprite_sheet_url'],
                                'sprite_position': image_info['sprite_position'],
                                'image_dimensions': image_info['dimensions'],"""
    
    if old_product_line in content:
        content = content.replace(old_product_line, new_product_lines)
        print("✅ Added sprite info to product data!")
    
    # Update logging
    old_log = 'self.logger.info(f"✅ IMAGE FOUND for {product_name}: {image_url}")'
    new_log = '''if image_info['sprite_sheet_url']:
                                self.logger.info(f"✅ SPRITE IMAGE found for {product_name}: Position {image_info['sprite_position']}")
                            elif image_info['image_url']:
                                self.logger.info(f"✅ DIRECT IMAGE found for {product_name}: {image_info['image_url']}")
                            else:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")'''
    
    if old_log in content:
        content = content.replace(old_log, new_log)
        print("✅ Enhanced logging!")
    
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(content)

def main():
    print("🖼️ Adding Enhanced Image Extraction Methods")
    print("=" * 50)
    
    # Add new methods
    add_enhanced_image_methods()
    
    # Update existing method
    update_existing_method()
    
    print("\n✅ Enhanced image extraction implemented!")
    print("\n🎯 What's added:")
    print("• _extract_sprite_image_info() method")
    print("• _extract_background_position() method") 
    print("• _extract_element_dimensions() method")
    print("• Enhanced product data with sprite info")
    print("• Better logging for sprite images")
    
    print("\n🚀 Try running:")
    print("python main.py")

if __name__ == "__main__":
    main()