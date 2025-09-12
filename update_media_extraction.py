#!/usr/bin/env python3
"""
Update the catalog scraper to:
1. Extract ALL images from carousel and thumbnails
2. Extract videos from iframe elements  
3. Remove English text from Shopify uploads
"""

def update_catalog_scraper():
    """Update the catalog scraper with better media extraction"""
    
    # Read current catalog scraper
    with open('scraper/wilo_catalog_scraper.py', 'r') as f:
        content = f.read()
    
    # Replace the extract_carousel_media method with enhanced version
    new_extract_media = '''    def extract_carousel_media(self):
        """Extract ALL images and videos from carousel and thumbnails - ENHANCED"""
        try:
            driver = self.browser_manager.get_driver()
            
            media_items = {
                'images': [],
                'videos': [],
                'all_media': []
            }
            
            # Extract from main carousel (role="listitem")
            print("🔍 Extracting from main carousel...")
            try:
                carousel_items = driver.find_elements(By.XPATH, "//div[@role='listitem']")
                print(f"Found {len(carousel_items)} carousel items")
                
                for i, item in enumerate(carousel_items):
                    try:
                        # Look for images in carousel item
                        imgs = item.find_elements(By.XPATH, ".//img[@src]")
                        for img in imgs:
                            src = img.get_attribute('src')
                            if src:
                                # Convert relative URLs to absolute
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                if src not in media_items['images']:
                                    media_items['images'].append(src)
                                    media_items['all_media'].append({
                                        'type': 'image',
                                        'url': src,
                                        'alt': img.get_attribute('alt') or f'Product Image {len(media_items["images"])}',
                                        'source': 'carousel'
                                    })
                                    print(f"   📸 Added carousel image {len(media_items['images'])}")
                        
                        # Look for videos in carousel item (iframe elements)
                        iframes = item.find_elements(By.XPATH, ".//iframe[@src]")
                        for iframe in iframes:
                            src = iframe.get_attribute('src')
                            if src and 'video' in src.lower():
                                # Convert relative URLs to absolute
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                if src not in media_items['videos']:
                                    media_items['videos'].append(src)
                                    media_items['all_media'].append({
                                        'type': 'video',
                                        'url': src,
                                        'title': f'Product Video {len(media_items["videos"])}',
                                        'source': 'carousel'
                                    })
                                    print(f"   🎥 Added carousel video {len(media_items['videos'])}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Error processing carousel item {i}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error extracting from carousel: {e}")
            
            # Extract from thumbnail section (cl-image-preview)
            print("🔍 Extracting from thumbnails...")
            try:
                thumbnail_imgs = driver.find_elements(By.XPATH, "//div[contains(@class, 'cl-image-preview')]//img[@src]")
                print(f"Found {len(thumbnail_imgs)} thumbnail images")
                
                for i, img in enumerate(thumbnail_imgs):
                    try:
                        src = img.get_attribute('src')
                        if src:
                            # Convert relative URLs to absolute
                            if src.startswith('//'):
                                src = f"https:{src}"
                            elif src.startswith('/'):
                                src = f"https://wilo.com{src}"
                            
                            # Add if not already present
                            if src not in media_items['images']:
                                media_items['images'].append(src)
                                media_items['all_media'].append({
                                    'type': 'image',
                                    'url': src,
                                    'alt': img.get_attribute('alt') or f'Product Thumbnail {len(media_items["images"])}',
                                    'source': 'thumbnail'
                                })
                                print(f"   📸 Added thumbnail image {len(media_items['images'])}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Error processing thumbnail {i}: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error extracting thumbnails: {e}")
            
            # Also look for any other images on the page
            print("🔍 Extracting additional images...")
            try:
                additional_selectors = [
                    "//img[contains(@src, 'wilo.com')]",
                    "//img[contains(@src, 'cms.media.wilo.com')]",
                    "//img[contains(@class, 'cl-img')]"
                ]
                
                for selector in additional_selectors:
                    try:
                        additional_imgs = driver.find_elements(By.XPATH, selector)
                        for img in additional_imgs:
                            src = img.get_attribute('src')
                            if src:
                                # Convert relative URLs to absolute
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                # Add if not already present
                                if src not in media_items['images']:
                                    media_items['images'].append(src)
                                    media_items['all_media'].append({
                                        'type': 'image',
                                        'url': src,
                                        'alt': img.get_attribute('alt') or f'Additional Image {len(media_items["images"])}',
                                        'source': 'additional'
                                    })
                                    print(f"   📸 Added additional image {len(media_items['images'])}")
                    except:
                        continue
                        
            except Exception as e:
                print(f"❌ Error extracting additional images: {e}")
            
            # Look for video thumbnails that might indicate videos
            print("🔍 Extracting video thumbnails...")
            try:
                video_thumbnail_selectors = [
                    "//img[contains(@src, 'still.jpg')]",
                    "//img[contains(@src, 'thumbnail') and contains(@src, 'video')]",
                    "//img[contains(@src, 'dcividpfinder')]"
                ]
                
                for selector in video_thumbnail_selectors:
                    try:
                        video_thumbs = driver.find_elements(By.XPATH, selector)
                        for thumb in video_thumbs:
                            src = thumb.get_attribute('src')
                            if src and 'still.jpg' in src:
                                # This is likely a video thumbnail
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                # Add as both image and potential video indicator
                                if src not in media_items['images']:
                                    media_items['images'].append(src)
                                    media_items['all_media'].append({
                                        'type': 'image',
                                        'url': src,
                                        'alt': f'Video Thumbnail {len(media_items["images"])}',
                                        'source': 'video_thumbnail'
                                    })
                                    print(f"   🎬 Added video thumbnail {len(media_items['images'])}")
                    except:
                        continue
                        
            except Exception as e:
                print(f"❌ Error extracting video thumbnails: {e}")
            
            print(f"📊 MEDIA EXTRACTION COMPLETE:")
            print(f"   📸 Total images: {len(media_items['images'])}")
            print(f"   🎥 Total videos: {len(media_items['videos'])}")
            print(f"   📁 Total media items: {len(media_items['all_media'])}")
            
            return media_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract media items: {e}")
            return {'images': [], 'videos': [], 'all_media': []}'''
    
    # Replace the method in the content
    import re
    pattern = r'def extract_carousel_media\(self\):.*?(?=\n    def |\Z)'
    content = re.sub(pattern, new_extract_media, content, flags=re.DOTALL)
    
    # Write back to file
    with open('scraper/wilo_catalog_scraper.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated catalog scraper with enhanced media extraction")

def update_shopify_config():
    """Remove English text from Shopify uploads"""
    
    # Read current shopify config
    with open('gui/widgets/shopify_config.py', 'r') as f:
        content = f.read()
    
    # Replace the create_product method to remove English text
    new_create_product = '''    def create_product(self, product_data):
        """Create a single product in Shopify - GERMAN ONLY VERSION"""
        try:
            print("=" * 80)
            print("🔍 SHOPIFY CREATE_PRODUCT DEBUG - GERMAN ONLY")
            print(f"Input product keys: {list(product_data.keys())}")
            
            # Extract data with debug logging
            name = product_data.get('name', 'Wilo Product')
            short_description = product_data.get('short_description', '')
            advantages = product_data.get('advantages', [])
            category = product_data.get('category', 'Industrie Heizung')
            subcategory = product_data.get('subcategory', 'Heizungspumpen')
            
            print(f"✅ Product name: '{name}'")
            print(f"📝 Short description length: {len(short_description)}")
            print(f"📝 Advantages count: {len(advantages)}")
            
            if short_description:
                print(f"📝 Description preview: '{short_description[:100]}...'")
            if advantages:
                print(f"📝 First advantage: '{advantages[0][:80]}...'")
            
            # BUILD GERMAN-ONLY SHOPIFY DESCRIPTION
            html_parts = []
            
            # Title
            html_parts.append(f"<h1>{name}</h1>")
            
            # REAL GERMAN DESCRIPTION ONLY
            if short_description and len(short_description.strip()) > 20:
                html_parts.append(f"<div class='product-description'><p>{short_description}</p></div>")
                print("✅ ADDED REAL GERMAN DESCRIPTION")
            else:
                # German fallback instead of English
                html_parts.append(f"<p>Professionelle {name} von Wilo für industrielle Heizungsanwendungen.</p>")
                print("⚠️ USED GERMAN FALLBACK DESCRIPTION")
            
            # Product info in German
            html_parts.append(f"<p><strong>Anwendung:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Produkttyp:</strong> {subcategory}</p>")
            
            # REAL GERMAN ADVANTAGES
            if advantages and len(advantages) > 0:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    if advantage and len(advantage.strip()) > 10:
                        html_parts.append(f"<li>{advantage.strip()}</li>")
                html_parts.append("</ul>")
                print(f"✅ ADDED {len(advantages)} REAL GERMAN ADVANTAGES")
            else:
                # German features instead of English
                html_parts.append("<h3>Hauptmerkmale</h3>")
                html_parts.append("<ul>")
                html_parts.append("<li>Hochwertige deutsche Ingenieurskunst</li>")
                html_parts.append("<li>Energieeffizienter Betrieb</li>")
                html_parts.append("<li>Zuverlässige Leistung für industrielle Anwendungen</li>")
                html_parts.append("<li>Professionelle Komponenten</li>")
                html_parts.append("</ul>")
                print("⚠️ USED GERMAN GENERIC FEATURES")
            
            # German brand info instead of English
            html_parts.append("<h3>Über Wilo</h3>")
            html_parts.append("<p>Wilo ist ein führender globaler Hersteller von Pumpen und Pumpensystemen für Heizung, Kühlung, Klimatechnik, Wasserversorgung und Abwasserbehandlung.</p>")
            
            # Build final description
            body_html = "\\n".join(html_parts)
            
            # Create Shopify product structure
            shopify_product = {
                'title': name,
                'body_html': body_html,
                'vendor': 'Wilo',
                'product_type': subcategory,
                'tags': f"Wilo, {category}, {subcategory}, Deutsche Qualität",
                'status': 'draft',
                'variants': [{
                    'title': 'Standard',
                    'price': '0.00',
                    'inventory_management': 'shopify',
                    'inventory_quantity': 0,
                    'requires_shipping': True,
                    'taxable': True,
                    'sku': f"WILO-{name.replace(' ', '-').replace('.', '').upper()[:20]}"
                }],
                'options': [{
                    'name': 'Ausführung',
                    'values': ['Standard']
                }]
            }
            
            # ENHANCED IMAGE HANDLING - Add ALL extracted images
            valid_images = []
            card_image = product_data.get('card_image_url', '')
            product_images = product_data.get('product_images', [])
            
            print(f"🔍 Processing ALL images: card={bool(card_image)}, product_images={len(product_images)}")
            
            # Validate card image
            if card_image:
                validated_card = self._validate_image_url(card_image)
                if validated_card:
                    valid_images.append({
                        'src': validated_card,
                        'alt': f"{name} - Produktbild"
                    })
                    print("🖼️ Added validated card image")
                else:
                    print(f"⚠️ Skipped invalid card image: {card_image[:100]}")
            
            # Validate ALL product images (increased limit)
            for i, img_url in enumerate(product_images[:15]):  # Increased from 8 to 15
                if img_url:
                    validated_img = self._validate_image_url(img_url)
                    if validated_img and validated_img not in [img['src'] for img in valid_images]:
                        valid_images.append({
                            'src': validated_img,
                            'alt': f"{name} - Bild {i+1}"
                        })
                        print(f"🖼️ Added validated product image {i+1}")
                    else:
                        print(f"⚠️ Skipped invalid product image {i+1}: {img_url[:100] if img_url else 'Empty URL'}")
            
            # Add valid images to product
            if valid_images:
                shopify_product['images'] = valid_images
                print(f"✅ Total valid images added: {len(valid_images)}")
            else:
                print("⚠️ No valid images found - creating product without images")
            
            # Create product via API
            payload = {'product': shopify_product}
            response = requests.post(
                f"{self.base_url}/products.json",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print("=" * 80)
            print(f"✅ GERMAN SHOPIFY PRODUCT READY:")
            print(f"   - Title: {name}")
            print(f"   - Description length: {len(body_html)}")
            print(f"   - Images: {len(valid_images)}")
            print(f"   - Language: GERMAN ONLY")
            print(f"   - Real content: {'YES' if short_description or advantages else 'NO'}")
            print("=" * 80)
            
            if response.status_code == 201:
                created_product = response.json()['product']
                print(f"✅ Successfully created German product in Shopify: {created_product['id']}")
                return created_product
            else:
                print(f"❌ Shopify API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating product: {e}")
            import traceback
            traceback.print_exc()
            return None'''
    
    # Replace the create_product method
    import re
    pattern = r'def create_product\(self, product_data\):.*?(?=\nclass |\n    def _validate_image_url|\Z)'
    content = re.sub(pattern, new_create_product, content, flags=re.DOTALL)
    
    # Write back to file
    with open('gui/widgets/shopify_config.py', 'w') as f:
        f.write(content)
    
    print("✅ Updated Shopify config to use German-only text")

def main():
    """Apply all updates"""
    print("🔧 UPDATING MEDIA EXTRACTION AND REMOVING ENGLISH TEXT")
    print("=" * 60)
    
    print("Applying updates:")
    print("1. Enhanced media extraction (ALL images + videos)")
    print("2. Remove English text from Shopify uploads")
    print("3. Better carousel and thumbnail parsing")
    
    try:
        # Update catalog scraper
        update_catalog_scraper()
        
        # Update shopify config
        update_shopify_config()
        
        print("\n✅ ALL UPDATES COMPLETED!")
        
        print("\n🎯 Media extraction improvements:")
        print("• Extracts from carousel items (role='listitem')")
        print("• Extracts from thumbnail section (cl-image-preview)")
        print("• Finds videos in iframe elements") 
        print("• Gets video thumbnails (still.jpg files)")
        print("• Processes up to 15 images per product")
        print("• Detailed logging of extraction process")
        
        print("\n🇩🇪 German-only Shopify content:")
        print("• Removed all English predefined text")
        print("• German fallback descriptions")
        print("• German section headers ('Ihre Vorteile', 'Über Wilo')")
        print("• German product info ('Anwendung', 'Produkttyp')")
        print("• German image alt text")
        
        print("\n🚀 Test the updated workflow:")
        print("1. python main.py")
        print("2. Extract products (will get ALL images + videos)")
        print("3. Upload to Shopify (German content only)")
        
        print("\n📊 Expected results:")
        print("✅ More images per product (10+ instead of 2-3)")
        print("✅ Video extraction working") 
        print("✅ Pure German content in Shopify")
        print("✅ No more English mixed with German")
        
    except Exception as e:
        print(f"\n❌ Error during updates: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()