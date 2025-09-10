#!/usr/bin/env python3
"""
Final comprehensive fix for both issues:
1. Fix stale element reference for second card
2. Fix Shopify upload to use ACTUAL extracted data
"""

def fix_stale_element_issue():
    """Fix the stale element reference issue in catalog scraper"""
    
    with open('scraper/wilo_catalog_scraper.py', 'r') as f:
        content = f.read()
    
    # Enhanced card processing method that handles stale elements
    enhanced_card_processing = '''    def _extract_products_from_cards(self, max_products):
        """Extract products from card elements - FIXED for stale elements"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            
            time.sleep(5)
            
            card_selectors = [
                "//div[contains(@class, 'card cl-overview h-100 rebrush')]",
                "//div[contains(@class, 'card') and contains(@class, 'cl-overview')]"
            ]
            
            all_products = []
            
            for i in range(max_products):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Processing product card {i+1}/{max_products}")
                
                try:
                    self.logger.info(f"=== PROCESSING CARD {i+1} ===")
                    
                    # RE-FIND cards each time to avoid stale element reference
                    cards = []
                    for selector in card_selectors:
                        try:
                            found_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, selector)))
                            if found_cards and len(found_cards) > i:
                                cards = found_cards
                                self.logger.info(f"Re-found {len(cards)} cards for iteration {i+1}")
                                break
                        except TimeoutException:
                            continue
                    
                    if not cards or len(cards) <= i:
                        self.logger.warning(f"No card found at position {i+1}")
                        break
                    
                    card = cards[i]  # Get the specific card for this iteration
                    
                    # Extract card data (this creates a simple data structure, no element references)
                    card_data = self._extract_card_data_safe(card, i)
                    
                    if card_data:
                        # Click and extract details (pass the fresh card element)
                        product_detail = self._get_product_details_safe(card, card_data, i)
                        
                        if product_detail:
                            all_products.append(product_detail)
                            
                            if self.products_callback:
                                self.products_callback(product_detail)
                            
                            self.logger.info(f"✅ Successfully extracted: {product_detail['name']}")
                        else:
                            self.logger.warning(f"❌ Failed to get details for card {i+1}")
                    else:
                        self.logger.warning(f"❌ Failed to extract card data for card {i+1}")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing card {i+1}: {e}")
                    continue
            
            self.logger.info(f"=== EXTRACTION COMPLETE ===")
            self.logger.info(f"Successfully processed {len(all_products)} out of {max_products} cards")
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from cards: {e}")
            return []
    
    def _extract_card_data_safe(self, card, index):
        """Extract basic data from card - SAFE version that doesn't store element references"""
        try:
            product_name = f"Product {index + 1}"
            
            image_url = ""
            try:
                img_element = card.find_element(By.XPATH, ".//img")
                img_src = img_element.get_attribute('src')
                if img_src:
                    if img_src.startswith('//'):
                        image_url = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        image_url = f"https://wilo.com{img_src}"
                    else:
                        image_url = img_src
            except:
                self.logger.debug(f"Could not find image in card {index+1}")
            
            product_link = ""
            link_selectors = [
                ".//a[@class='stretched-link']",
                ".//a[contains(@class, 'stretched')]",
                ".//a[@href]"
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
            
            card_data = {
                'name': product_name,
                'card_image_url': image_url,
                'product_link': product_link,
                'card_index': index
                # NOTE: NO element references stored to avoid stale element issues
            }
            
            self.logger.info(f"Extracted card data for position {index+1}")
            return card_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract card data: {e}")
            return {
                'name': f"Product {index + 1}",
                'card_image_url': '',
                'product_link': '',
                'card_index': index
            }
    
    def _get_product_details_safe(self, card, card_data, index):
        """Click on card and extract product details - SAFE version"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Try clicking via link first
            clicked = False
            if card_data.get('product_link'):
                try:
                    link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                    driver.execute_script("arguments[0].click();", link_element)
                    self.logger.info(f"Clicked via link for card {index+1}")
                    clicked = True
                except Exception as e:
                    self.logger.warning(f"Link click failed: {e}")
            
            # If link click failed, try clicking the card itself
            if not clicked:
                try:
                    driver.execute_script("arguments[0].click();", card)
                    self.logger.info(f"Clicked directly on card {index+1}")
                    clicked = True
                except Exception as e:
                    self.logger.error(f"Direct card click failed: {e}")
            
            if not clicked:
                self.logger.error(f"Could not click card {index+1}")
                return None
            
            time.sleep(5)
            self.browser_manager.take_screenshot(f"catalog_product_{index}_page.png")
            
            product_details = self._extract_product_page_details(card_data)
            
            driver.back()
            time.sleep(3)
            
            return product_details
            
        except Exception as e:
            self.logger.error(f"Failed to get product details: {e}")
            return None'''
    
    # Replace the methods
    import re
    
    # Replace _extract_products_from_cards
    pattern1 = r'def _extract_products_from_cards\(self, max_products\):.*?(?=\n    def |\Z)'
    content = re.sub(pattern1, enhanced_card_processing, content, flags=re.DOTALL)
    
    with open('scraper/wilo_catalog_scraper.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed stale element reference issue")

def fix_shopify_upload_data_usage():
    """Fix Shopify upload to actually use the extracted data"""
    
    with open('gui/widgets/shopify_config.py', 'r') as f:
        content = f.read()
    
    # Find and completely replace the entire _transform_to_shopify_format method
    new_transform_method = '''    def _transform_to_shopify_format(self, wilo_product: Dict) -> Dict:
        """Transform Wilo product data to Shopify format - ACTUALLY USES EXTRACTED DATA"""
        try:
            # FORCE DEBUG LOGGING
            self.logger.info(f"🔍 TRANSFORMING PRODUCT DATA:")
            self.logger.info(f"   Product name: {wilo_product.get('name', 'N/A')}")
            self.logger.info(f"   Short description length: {len(wilo_product.get('short_description', ''))}")
            self.logger.info(f"   Advantages count: {len(wilo_product.get('advantages', []))}")
            self.logger.info(f"   Product images count: {len(wilo_product.get('product_images', []))}")
            
            # Extract ACTUAL data
            name = wilo_product.get('name', 'Wilo Pump')
            category = wilo_product.get('category', 'Pumps')
            subcategory = wilo_product.get('subcategory', 'Standard')
            
            # Get REAL content
            short_description = wilo_product.get('short_description', '')
            advantages = wilo_product.get('advantages', [])
            long_description = wilo_product.get('long_description', '')
            
            self.logger.info(f"   Using short_description: {short_description[:100]}...")
            self.logger.info(f"   Using advantages: {advantages[:2] if advantages else 'None'}")
            
            # Build ACTUAL description using REAL data
            body_html = self._build_real_description(name, short_description, advantages, long_description, category, subcategory)
            
            self.logger.info(f"   Built description length: {len(body_html)}")
            
            # Create Shopify product with REAL data
            shopify_product = {
                'title': name,
                'body_html': body_html,
                'vendor': 'Wilo',
                'product_type': subcategory,
                'tags': f"Wilo, {category}, {subcategory}",
                'status': 'draft',
                'variants': [{
                    'title': 'Default',
                    'price': '0.00',
                    'inventory_management': 'shopify',
                    'inventory_quantity': 0,
                    'requires_shipping': True,
                    'taxable': True,
                    'sku': f"WILO-{name.replace(' ', '-').replace('.', '').upper()[:20]}"
                }],
                'options': [{
                    'name': 'Title',
                    'values': ['Default']
                }]
            }
            
            # Add REAL images
            images = []
            
            # Card image
            if wilo_product.get('card_image_url'):
                images.append({
                    'src': wilo_product['card_image_url'],
                    'alt': f"{name} - Card Image"
                })
                self.logger.info(f"   Added card image: {wilo_product['card_image_url']}")
            
            # Product images
            product_images = wilo_product.get('product_images', [])
            for i, img_url in enumerate(product_images[:5]):  # Max 5 additional images
                if img_url and img_url not in [img['src'] for img in images]:
                    images.append({
                        'src': img_url,
                        'alt': f"{name} - Image {i+1}"
                    })
                    self.logger.info(f"   Added product image {i+1}: {img_url}")
            
            if images:
                shopify_product['images'] = images
                self.logger.info(f"   Total images added: {len(images)}")
            
            self.logger.info(f"✅ SHOPIFY PRODUCT READY with {len(body_html)} char description and {len(images)} images")
            
            return shopify_product
            
        except Exception as e:
            self.logger.error(f"❌ Error transforming product data: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {}
    
    def _build_real_description(self, name, short_description, advantages, long_description, category, subcategory):
        """Build description using ONLY the real extracted data"""
        html_parts = []
        
        # Product title
        html_parts.append(f"<h2>{name}</h2>")
        
        # REAL short description (1013 characters from your logs)
        if short_description and len(short_description) > 50:
            html_parts.append(f"<div class='product-description'>{short_description}</div>")
            self.logger.info(f"   ✅ Added REAL short description ({len(short_description)} chars)")
        else:
            html_parts.append(f"<p>Professional {name} from Wilo for industrial applications.</p>")
            self.logger.warning(f"   ⚠️ Used fallback description (short desc only {len(short_description)} chars)")
        
        # Category info
        html_parts.append(f"<p><strong>Category:</strong> {category}</p>")
        html_parts.append(f"<p><strong>Type:</strong> {subcategory}</p>")
        
        # REAL advantages (9 items from your logs)
        if advantages and len(advantages) > 0:
            html_parts.append("<h3>Ihre Vorteile (Product Advantages)</h3>")
            html_parts.append("<ul>")
            for advantage in advantages:
                if advantage and len(advantage.strip()) > 5:
                    html_parts.append(f"<li>{advantage.strip()}</li>")
            html_parts.append("</ul>")
            self.logger.info(f"   ✅ Added {len(advantages)} REAL advantages")
        else:
            # ONLY as absolute fallback
            html_parts.append("<h3>Features</h3>")
            html_parts.append("<ul>")
            html_parts.append("<li>High-quality German engineering</li>")
            html_parts.append("<li>Energy-efficient operation</li>")
            html_parts.append("<li>Reliable performance</li>")
            html_parts.append("<li>Professional grade components</li>")
            html_parts.append("</ul>")
            self.logger.warning(f"   ⚠️ Used fallback features (no real advantages found)")
        
        # Long description if available
        if long_description and len(long_description) > 30:
            html_parts.append("<h3>Product Details</h3>")
            paragraphs = long_description.split('\\n\\n')
            for paragraph in paragraphs:
                if paragraph.strip() and len(paragraph.strip()) > 10:
                    html_parts.append(f"<p>{paragraph.strip()}</p>")
            self.logger.info(f"   ✅ Added long description ({len(long_description)} chars)")
        
        # Brand info
        html_parts.append("<h3>About Wilo</h3>")
        html_parts.append("<p>Wilo is a leading global manufacturer of pumps and pump systems for heating, cooling, air conditioning, water supply, and wastewater treatment.</p>")
        
        final_html = "\\n".join(html_parts)
        self.logger.info(f"   📝 Final description built: {len(final_html)} characters")
        
        return final_html'''
    
    # Replace the method
    import re
    pattern = r'def _transform_to_shopify_format\(self, wilo_product: Dict\) -> Dict:.*?(?=\n    def |\n\nclass |\Z)'
    new_content = re.sub(pattern, new_transform_method, content, flags=re.DOTALL)
    
    with open('gui/widgets/shopify_config.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed Shopify upload to FORCE use of actual extracted data")

def main():
    """Main comprehensive fix"""
    print("🔧 FINAL COMPREHENSIVE FIX - BOTH ISSUES")
    print("=" * 50)
    
    try:
        # Fix 1: Stale element reference
        fix_stale_element_issue()
        
        # Fix 2: Shopify upload using real data
        fix_shopify_upload_data_usage()
        
        print("\\n✅ BOTH ISSUES FIXED!")
        print("\\n🎯 Issue 1 Fixed: Stale Element Reference")
        print("• Re-finds cards for each iteration")
        print("• No stored element references")
        print("• Both cards should work now")
        
        print("\\n🎯 Issue 2 Fixed: Shopify Upload Data")
        print("• FORCES use of actual extracted data")
        print("• Comprehensive debug logging")
        print("• Real 1013-character descriptions")
        print("• Real 9-item advantages lists")
        print("• Multiple product images")
        
        print("\\n🚀 Test Results Expected:")
        print("python main.py")
        print("\\n📋 Extraction Logs Expected:")
        print("Card 1: ✅ Wilo-Atmos TERA-SCH")
        print("Card 2: ✅ [Real Product Name]")
        print("\\n📋 Shopify Upload Logs Expected:")
        print("🔍 TRANSFORMING PRODUCT DATA:")
        print("   Product name: Wilo-Atmos TERA-SCH")
        print("   Short description length: 1013")
        print("   Advantages count: 9")
        print("   ✅ Added REAL short description")
        print("   ✅ Added 9 REAL advantages")
        print("\\n📋 Shopify Content Expected:")
        print("Title: Wilo-Atmos TERA-SCH")
        print("Description: Real 1013-char description + real advantages")
        print("Images: Card image + 2 product images")
        
        print("\\n⚠️ CRITICAL: Watch the logs!")
        print("You should see detailed transformation logs showing real data being used!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())