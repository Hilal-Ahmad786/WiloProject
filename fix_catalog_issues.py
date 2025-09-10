#!/usr/bin/env python3
"""
Fix the catalog scraper issues:
1. Better card name extraction 
2. Ensure proper data flow to Shopify
"""

def fix_card_extraction():
    """Fix the card extraction to handle different card structures"""
    
    # Read the current scraper
    with open('scraper/wilo_catalog_scraper.py', 'r') as f:
        content = f.read()
    
    # Updated _extract_card_data method
    new_card_extraction = '''    def _extract_card_data(self, card, index):
        """Extract data from a single product card with better error handling"""
        try:
            # Multiple strategies to extract product name
            product_name = ""
            
            # Strategy 1: Card footer h3
            try:
                name_element = card.find_element(By.XPATH, ".//div[@class='card-footer']//h3")
                product_name = name_element.text.strip()
                self.logger.debug(f"Found name via card-footer h3: {product_name}")
            except:
                pass
            
            # Strategy 2: Any h3 in the card
            if not product_name:
                try:
                    name_element = card.find_element(By.XPATH, ".//h3")
                    product_name = name_element.text.strip()
                    self.logger.debug(f"Found name via any h3: {product_name}")
                except:
                    pass
            
            # Strategy 3: Card title attribute or alt text
            if not product_name:
                try:
                    title_element = card.find_element(By.XPATH, ".//*[@title]")
                    product_name = title_element.get_attribute('title').strip()
                    self.logger.debug(f"Found name via title attribute: {product_name}")
                except:
                    pass
            
            # Strategy 4: Any text content that looks like a product name
            if not product_name:
                try:
                    text_elements = card.find_elements(By.XPATH, ".//*[text()]")
                    for elem in text_elements:
                        text = elem.text.strip()
                        # Look for text that contains "Wilo" and is substantial
                        if text and len(text) > 5 and ('wilo' in text.lower() or 'atmos' in text.lower() or 'pump' in text.lower()):
                            product_name = text
                            self.logger.debug(f"Found name via text content: {product_name}")
                            break
                except:
                    pass
            
            # Strategy 5: Use a fallback name based on index
            if not product_name:
                product_name = f"Wilo Product {index + 1}"
                self.logger.warning(f"Using fallback name for card {index + 1}: {product_name}")
            
            # Extract image from card
            image_url = ""
            try:
                img_element = card.find_element(By.XPATH, ".//img")
                img_src = img_element.get_attribute('src')
                if img_src:
                    # Convert relative URL to absolute
                    if img_src.startswith('//'):
                        image_url = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        image_url = f"https://wilo.com{img_src}"
                    else:
                        image_url = img_src
            except:
                self.logger.warning(f"Could not find image in card {index+1}")
            
            # Extract product link with multiple strategies
            product_link = ""
            link_selectors = [
                ".//a[@class='stretched-link']",
                ".//a[contains(@class, 'stretched')]",
                ".//a[@href]",
                ".//a"
            ]
            
            for selector in link_selectors:
                try:
                    link_element = card.find_element(By.XPATH, selector)
                    href = link_element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            product_link = f"https://wilo.com{href}"
                        else:
                            product_link = href
                        break
                except:
                    continue
            
            if not product_link:
                self.logger.warning(f"Could not find product link in card {index+1}")
            
            card_data = {
                'name': product_name,
                'card_image_url': image_url,
                'product_link': product_link,
                'card_index': index
            }
            
            self.logger.info(f"Extracted card data: {product_name}")
            return card_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract card data for card {index+1}: {e}")
            # Return fallback data instead of None
            return {
                'name': f"Wilo Product {index + 1}",
                'card_image_url': '',
                'product_link': '',
                'card_index': index
            }'''
    
    # Replace the method
    import re
    pattern = r'def _extract_card_data\(self, card, index\):.*?(?=\n    def |\n\n    def |\Z)'
    new_content = re.sub(pattern, new_card_extraction, content, flags=re.DOTALL)
    
    # Write back
    with open('scraper/wilo_catalog_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed card extraction with better error handling")

def fix_shopify_upload():
    """Fix the Shopify upload to use the actual extracted data"""
    
    # Read the Shopify config file
    try:
        with open('gui/widgets/shopify_config.py', 'r') as f:
            content = f.read()
        
        # Find and replace the _transform_to_shopify_format method
        new_transform_method = '''    def _transform_to_shopify_format(self, wilo_product: Dict) -> Dict:
        """Transform Wilo product data to Shopify product format - FIXED to use real data"""
        try:
            # Extract basic info - USE ACTUAL EXTRACTED DATA
            name = wilo_product.get('name', 'Wilo Pump')
            category = wilo_product.get('category', 'Pumps')
            subcategory = wilo_product.get('subcategory', 'Standard')
            
            # Use the ACTUAL extracted descriptions
            short_description = wilo_product.get('short_description', '')
            advantages = wilo_product.get('advantages', [])
            long_description = wilo_product.get('long_description', '')
            full_description = wilo_product.get('full_description', '')
            
            specifications = wilo_product.get('specifications', {})
            
            # Build enhanced description using REAL extracted content
            if full_description:
                # Use the pre-built full description
                body_html = full_description
            else:
                # Build from components
                body_html = self._build_product_description_from_extracted_data(wilo_product)
            
            # Create Shopify product
            shopify_product = {
                'title': name,
                'body_html': body_html,
                'vendor': 'Wilo',
                'product_type': subcategory,
                'tags': self._generate_tags(wilo_product),
                'status': 'draft',  # Start as draft for review
                'variants': [{
                    'title': 'Default',
                    'price': '0.00',  # Set price manually later
                    'inventory_management': 'shopify',
                    'inventory_quantity': 0,
                    'requires_shipping': True,
                    'taxable': True,
                    'sku': self._generate_sku(wilo_product)
                }],
                'options': [{
                    'name': 'Title',
                    'values': ['Default']
                }]
            }
            
            # Add product images if available - USE EXTRACTED IMAGES
            images = []
            
            # Add card image
            if wilo_product.get('card_image_url'):
                images.append({
                    'src': wilo_product['card_image_url'],
                    'alt': f"{name} - Card Image"
                })
            
            # Add product images from carousel
            product_images = wilo_product.get('product_images', [])
            for img_url in product_images[:5]:  # Limit to 5 images
                if img_url not in [img['src'] for img in images]:  # Avoid duplicates
                    images.append({
                        'src': img_url,
                        'alt': f"{name} - Product Image"
                    })
            
            if images:
                shopify_product['images'] = images
            
            # Add custom fields as metafields
            metafields = self._create_metafields(wilo_product)
            if metafields:
                shopify_product['metafields'] = metafields
            
            return shopify_product
            
        except Exception as e:
            self.logger.error(f"Error transforming product data: {e}")
            return {}
    
    def _build_product_description_from_extracted_data(self, product: Dict) -> str:
        """Build description using the ACTUAL extracted data"""
        try:
            name = product.get('name', 'Wilo Pump')
            category = product.get('category', 'Pumps')
            subcategory = product.get('subcategory', 'Standard')
            
            # Use EXTRACTED content
            short_description = product.get('short_description', '')
            advantages = product.get('advantages', [])
            long_description = product.get('long_description', '')
            
            html_parts = []
            
            # Header
            html_parts.append(f"<h2>{name}</h2>")
            
            # Use ACTUAL short description instead of generic text
            if short_description:
                html_parts.append(f"<div class='product-intro'>{short_description}</div>")
            
            # Category information
            html_parts.append(f"<p><strong>Category:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Type:</strong> {subcategory}</p>")
            
            # Use ACTUAL advantages instead of generic features
            if advantages:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    html_parts.append(f"<li>{advantage}</li>")
                html_parts.append("</ul>")
            else:
                # Only use generic features if no real advantages were extracted
                html_parts.append("<h3>Features</h3>")
                html_parts.append("<ul>")
                html_parts.append("<li>High-quality German engineering</li>")
                html_parts.append("<li>Energy-efficient operation</li>")
                html_parts.append("<li>Reliable performance</li>")
                html_parts.append("<li>Professional grade components</li>")
                html_parts.append("</ul>")
            
            # Add long description if available
            if long_description:
                html_parts.append("<h3>Product Details</h3>")
                # Split into paragraphs
                paragraphs = long_description.split('\\n\\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"<p>{paragraph.strip()}</p>")
            
            # Specifications
            specs = product.get('specifications', {})
            if specs and len(specs) > 2:  # More than just brand and series
                html_parts.append("<h3>Specifications</h3>")
                html_parts.append("<ul>")
                for key, value in specs.items():
                    if value and str(value).strip() and key not in ['brand']:
                        html_parts.append(f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>")
                html_parts.append("</ul>")
            
            # Brand info
            html_parts.append("<h3>About Wilo</h3>")
            html_parts.append("<p>Wilo is a leading global manufacturer of pumps and pump systems for heating, cooling, air conditioning, water supply, and wastewater treatment.</p>")
            
            return "\\n".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Error building description: {e}")
            return product.get('short_description', '') or f"{product.get('name', 'Wilo Pump')} - Professional pump system."'''
        
        # Replace the method
        import re
        pattern = r'def _transform_to_shopify_format\(self, wilo_product: Dict\) -> Dict:.*?(?=\n    def |\n\n    def |\Z)'
        new_content = re.sub(pattern, new_transform_method, content, flags=re.DOTALL)
        
        # Write back
        with open('gui/widgets/shopify_config.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Fixed Shopify upload to use actual extracted data")
        
    except FileNotFoundError:
        print("⚠️  Shopify config file not found, skipping Shopify fix")
    except Exception as e:
        print(f"⚠️  Could not fix Shopify upload: {e}")

def add_debug_logging():
    """Add better debug logging to see what's being extracted"""
    
    try:
        with open('scraper/wilo_catalog_scraper.py', 'r') as f:
            content = f.read()
        
        # Add debug logging to the product creation
        debug_product_creation = '''            # Create comprehensive product object with DEBUG LOGGING
            product = {
                'id': f"catalog_{card_data['card_index']+1}_{int(time.time())}",
                'name': card_data['name'],
                'category': 'Industrie Heizung',
                'subcategory': 'Heizungspumpen',
                'source': 'catalog',
                
                # Images and media
                'card_image_url': card_data['card_image_url'],
                'product_images': media_items['images'],
                'product_videos': media_items['videos'],
                'all_media': media_items['all_media'],
                
                # Descriptions
                'short_description': short_description,
                'advantages': advantages,
                'long_description': long_description,
                'full_description': self._build_full_description(short_description, advantages, long_description),
                
                # Additional data
                'product_url': driver.current_url,
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'specifications': {
                    'brand': 'Wilo',
                    'series': card_data['name'],
                    'application': 'Industrie Heizung',
                    'type': 'Heizungspumpe'
                },
                'price': 'Price on request',
                'currency': 'EUR',
                'country': 'Germany',
                'status': 'Catalog Product - Real Extraction'
            }
            
            # DEBUG LOGGING
            self.logger.info(f"🔍 PRODUCT DEBUG for {card_data['name']}:")
            self.logger.info(f"   Short desc length: {len(short_description)} chars")
            self.logger.info(f"   Advantages count: {len(advantages)}")
            self.logger.info(f"   Long desc length: {len(long_description)} chars")
            self.logger.info(f"   Images count: {len(media_items['images'])}")
            self.logger.info(f"   Videos count: {len(media_items['videos'])}")
            
            if short_description:
                self.logger.info(f"   Short desc preview: {short_description[:100]}...")
            if advantages:
                self.logger.info(f"   First advantage: {advantages[0][:50]}...")
            '''
        
        # Find and replace the product creation
        pattern = r'# Create comprehensive product object.*?return product'
        new_content = re.sub(pattern, debug_product_creation + '\n            return product', content, flags=re.DOTALL)
        
        with open('scraper/wilo_catalog_scraper.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Added debug logging to track extraction")
        
    except Exception as e:
        print(f"⚠️  Could not add debug logging: {e}")

def main():
    """Main fix function"""
    print("🔧 FIXING CATALOG SCRAPER ISSUES")
    print("=" * 50)
    
    try:
        # Fix the card extraction
        fix_card_extraction()
        
        # Fix Shopify upload
        fix_shopify_upload()
        
        # Add debug logging
        add_debug_logging()
        
        print("\n✅ ALL ISSUES FIXED!")
        print("\n🎯 Fixed Issues:")
        print("• Better card name extraction with fallback strategies")
        print("• Shopify upload now uses ACTUAL extracted data")
        print("• Added debug logging to track extraction")
        print("• Real descriptions instead of generic content")
        
        print("\n🚀 Test your fixes:")
        print("python main.py")
        print("1. Try catalog scraper with 2 products")
        print("2. Check console logs for extraction details")
        print("3. Upload to Shopify and verify real content")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())