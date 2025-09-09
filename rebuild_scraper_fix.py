#!/usr/bin/env python3
"""
Rebuild the problematic section of wilo_scraper.py with correct indentation
"""

def rebuild_scraper_section():
    """Rebuild the image extraction section with proper indentation"""
    
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # Find the problematic area and replace it entirely
    # Look for the start of the image extraction in the method
    start_marker = "# ENHANCED SPRITE SHEET IMAGE EXTRACTION"
    end_marker = "except Exception as row_error:"
    
    if start_marker in content and end_marker in content:
        start_pos = content.find(start_marker)
        end_pos = content.find(end_marker, start_pos)
        
        if start_pos != -1 and end_pos != -1:
            # Replace the entire problematic section
            replacement_section = '''# ENHANCED IMAGE EXTRACTION
                            image_url = ""
                            try:
                                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                                style_attr = img_div.get_attribute('style')
                                if 'url(' in style_attr:
                                    start = style_attr.find('url("') + 5
                                    end = style_attr.find('")', start)
                                    if start > 4 and end > start:
                                        relative_url = style_attr[start:end]
                                        # Decode HTML entities
                                        relative_url = relative_url.replace('&quot;', '"').replace('&amp;', '&')
                                        # Convert to absolute URL
                                        if relative_url.startswith('ApplRangeHandler'):
                                            image_url = f"https://select.wilo.com/{relative_url}"
                                        else:
                                            image_url = relative_url
                                        self.logger.info(f"✅ IMAGE FOUND for {product_name}: {image_url}")
                            except:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")
                            
                            '''
            
            new_content = content[:start_pos] + replacement_section + content[end_pos:]
            
            with open('scraper/wilo_scraper.py', 'w') as f:
                f.write(new_content)
            
            print("✅ Rebuilt problematic section with correct indentation!")
            return True
    
    return False

def simple_fix_approach():
    """Simple approach - just fix the immediate syntax error"""
    
    with open('scraper/wilo_scraper.py', 'r') as f:
        lines = f.readlines()
    
    # Find and fix any lines with incorrect indentation around line 711
    fixed = False
    for i, line in enumerate(lines):
        # Look for the problematic logging lines
        if "SPRITE IMAGE found" in line or "DIRECT IMAGE found" in line or "NO IMAGE found" in line:
            # Check if it's improperly indented
            if not line.startswith('                                '):  # 32 spaces
                # Fix the indentation
                content = line.lstrip()
                lines[i] = '                                ' + content
                fixed = True
                print(f"Fixed line {i+1}: {content.strip()}")
    
    if fixed:
        with open('scraper/wilo_scraper.py', 'w') as f:
            f.writelines(lines)
        print("✅ Fixed indentation issues!")
        return True
    
    return False

def emergency_restore():
    """Emergency restore - go back to working version"""
    
    working_extraction_method = '''    def _extract_products_from_current_view(self, category, subcategory):
        """Extract products from current page view"""
        try:
            driver = self.browser_manager.get_driver()
            products = []
            
            self.browser_manager.take_screenshot(f"step8_products_{subcategory[:10]}.png")
            
            # Extract from grid rows
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
                            
                            # Extract image URL - FIXED VERSION
                            image_url = ""
                            try:
                                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                                style_attr = img_div.get_attribute('style')
                                if 'url(' in style_attr:
                                    start = style_attr.find('url("') + 5
                                    end = style_attr.find('")', start)
                                    if start > 4 and end > start:
                                        relative_url = style_attr[start:end]
                                        # Decode HTML entities
                                        relative_url = relative_url.replace('&quot;', '"').replace('&amp;', '&')
                                        # Convert to absolute URL
                                        if relative_url.startswith('ApplRangeHandler'):
                                            image_url = f"https://select.wilo.com/{relative_url}"
                                        else:
                                            image_url = relative_url
                                        self.logger.info(f"✅ IMAGE FOUND for {product_name}: {image_url}")
                            except:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")
                            
                            # Create product object
                            product = {
                                'id': f"{category.replace('.', '').replace(' ', '_')}_{subcategory.replace(' ', '_')}_{i+1}",
                                'name': product_name,
                                'category': category,
                                'subcategory': subcategory,
                                'image_url': image_url,
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
                                'has_image': bool(image_url)
                            }
                            
                            products.append(product)
                            self.logger.info(f"Enhanced extraction - Product: {product_name}")
                            
                        except Exception as row_error:
                            self.logger.error(f"Error processing row: {row_error}")
                            continue
                    
                    if products:
                        break
                        
                except Exception as selector_error:
                    self.logger.error(f"Error with selector {selector}: {selector_error}")
                    continue
            
            # Summary
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
'''
    
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # Replace the entire method
    import re
    pattern = r'def _extract_products_from_current_view\(self, category, subcategory\):.*?(?=\n    def |\n\nclass |\Z)'
    new_content = re.sub(pattern, working_extraction_method, content, flags=re.DOTALL)
    
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Restored to working version with HTML entity decoding!")

def main():
    print("🔧 Fixing Indentation Error in wilo_scraper.py")
    print("=" * 45)
    
    # Try different approaches
    if rebuild_scraper_section():
        print("✅ Method 1: Section rebuilt successfully!")
    elif simple_fix_approach():
        print("✅ Method 2: Simple fix applied!")
    else:
        print("⚠️ Trying emergency restore...")
        emergency_restore()
        print("✅ Method 3: Emergency restore completed!")
    
    print("\n🚀 Try running again:")
    print("python main.py")

if __name__ == "__main__":
    main()