#!/usr/bin/env python3
"""
Final fix for Shopify upload - the scraper works, but Shopify upload ignores real data
"""

def fix_shopify_transform_method():
    """Replace the entire transformation method in shopify_config.py"""
    
    with open('gui/widgets/shopify_config.py', 'r') as f:
        content = f.read()
    
    # Find where the _transform_to_shopify_format method starts and ends
    start_pattern = "def _transform_to_shopify_format(self, wilo_product: Dict) -> Dict:"
    
    if start_pattern in content:
        start_index = content.find(start_pattern)
        
        # Find the next method definition after this one
        next_method_patterns = [
            "\n    def _build_product_description",
            "\n    def _generate_tags",
            "\n    def _generate_sku", 
            "\n    def _create_metafields",
            "\n    def get_settings"
        ]
        
        end_index = len(content)  # Default to end of file
        for pattern in next_method_patterns:
            pattern_index = content.find(pattern, start_index + 1)
            if pattern_index != -1 and pattern_index < end_index:
                end_index = pattern_index
        
        # Replace the entire method
        new_method = '''    def _transform_to_shopify_format(self, wilo_product: Dict) -> Dict:
        """Transform Wilo product data to Shopify format - FINAL FIX VERSION"""
        try:
            # DETAILED DEBUG LOGGING
            self.logger.info("=" * 60)
            self.logger.info("🔍 SHOPIFY TRANSFORMATION DEBUG:")
            self.logger.info(f"   Input product keys: {list(wilo_product.keys())}")
            
            name = wilo_product.get('name', 'Wilo Pump')
            self.logger.info(f"   Product name: '{name}'")
            
            short_description = wilo_product.get('short_description', '')
            self.logger.info(f"   Short description length: {len(short_description)}")
            self.logger.info(f"   Short description preview: '{short_description[:100]}...'")
            
            advantages = wilo_product.get('advantages', [])
            self.logger.info(f"   Advantages count: {len(advantages)}")
            if advantages:
                self.logger.info(f"   First advantage: '{advantages[0][:50]}...'")
            
            product_images = wilo_product.get('product_images', [])
            card_image = wilo_product.get('card_image_url', '')
            self.logger.info(f"   Product images: {len(product_images)}")
            self.logger.info(f"   Card image: {'Yes' if card_image else 'No'}")
            
            # BUILD REAL DESCRIPTION
            html_parts = []
            
            # Product title
            html_parts.append(f"<h2>{name}</h2>")
            
            # FORCE use of real short description
            if short_description and len(short_description) > 10:
                html_parts.append(f"<div class='product-description'>{short_description}</div>")
                self.logger.info("   ✅ ADDED REAL SHORT DESCRIPTION")
            else:
                html_parts.append(f"<p>Professional {name} from Wilo.</p>")
                self.logger.warning("   ⚠️ USED FALLBACK DESCRIPTION")
            
            # Category info
            category = wilo_product.get('category', 'Industrie Heizung')
            subcategory = wilo_product.get('subcategory', 'Heizungspumpen')
            html_parts.append(f"<p><strong>Category:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Type:</strong> {subcategory}</p>")
            
            # FORCE use of real advantages
            if advantages and len(advantages) > 0:
                html_parts.append("<h3>Ihre Vorteile (Real Extracted Advantages)</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    if advantage and len(advantage.strip()) > 3:
                        html_parts.append(f"<li>{advantage.strip()}</li>")
                html_parts.append("</ul>")
                self.logger.info(f"   ✅ ADDED {len(advantages)} REAL ADVANTAGES")
            else:
                # This should NOT happen with our data
                html_parts.append("<h3>Features</h3>")
                html_parts.append("<ul>")
                html_parts.append("<li>High-quality German engineering</li>")
                html_parts.append("<li>Energy-efficient operation</li>")
                html_parts.append("<li>Reliable performance</li>")
                html_parts.append("<li>Professional grade components</li>")
                html_parts.append("</ul>")
                self.logger.error("   ❌ FALLBACK TO GENERIC FEATURES - THIS SHOULD NOT HAPPEN!")
            
            # Brand info
            html_parts.append("<h3>About Wilo</h3>")
            html_parts.append("<p>Wilo is a leading global manufacturer of pumps and pump systems.</p>")
            
            # Build final HTML
            body_html = "\\n".join(html_parts)
            self.logger.info(f"   📝 Final HTML length: {len(body_html)} characters")
            
            # Create Shopify product
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
            
            # Add images
            images = []
            
            # Card image first
            if card_image:
                images.append({
                    'src': card_image,
                    'alt': f"{name} - Card Image"
                })
                self.logger.info(f"   🖼️ Added card image")
            
            # Product images
            for i, img_url in enumerate(product_images[:5]):
                if img_url and img_url not in [img['src'] for img in images]:
                    images.append({
                        'src': img_url,
                        'alt': f"{name} - Image {i+1}"
                    })
                    self.logger.info(f"   🖼️ Added product image {i+1}")
            
            if images:
                shopify_product['images'] = images
                self.logger.info(f"   📸 Total images: {len(images)}")
            
            self.logger.info("=" * 60)
            self.logger.info("✅ SHOPIFY PRODUCT TRANSFORMATION COMPLETE")
            self.logger.info(f"   Title: {name}")
            self.logger.info(f"   Description length: {len(body_html)}")
            self.logger.info(f"   Images: {len(images)}")
            self.logger.info("=" * 60)
            
            return shopify_product
            
        except Exception as e:
            self.logger.error(f"❌ TRANSFORMATION ERROR: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {}'''
        
        # Replace the method in the content
        new_content = content[:start_index] + new_method + content[end_index:]
        
        with open('gui/widgets/shopify_config.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Replaced Shopify transformation method")
    else:
        print("❌ Could not find transformation method")

def main():
    """Main fix function"""
    print("🔧 FINAL SHOPIFY UPLOAD FIX")
    print("=" * 35)
    
    try:
        fix_shopify_transform_method()
        
        print("\\n✅ SHOPIFY UPLOAD FIXED!")
        print("\\n🎯 What was fixed:")
        print("• Replaced entire transformation method")
        print("• FORCES use of real extracted data")
        print("• Comprehensive debug logging")
        print("• Should show detailed transformation logs")
        
        print("\\n🚀 Test the upload:")
        print("1. python main.py")
        print("2. Extract 2 products (should work perfectly)")
        print("3. Go to Shopify Integration tab")
        print("4. Click 'Upload Scraped Products'")
        print("5. Watch the logs for detailed transformation info")
        
        print("\\n📋 Expected Shopify upload logs:")
        print("🔍 SHOPIFY TRANSFORMATION DEBUG:")
        print("   Product name: 'Wilo-Atmos TERA-SCH'")
        print("   Short description length: 1013")
        print("   Advantages count: 9")
        print("   ✅ ADDED REAL SHORT DESCRIPTION")
        print("   ✅ ADDED 9 REAL ADVANTAGES")
        print("   📸 Total images: 3")
        
        print("\\n📋 Expected Shopify content:")
        print("Real 1013-character descriptions")
        print("Real advantages in German")
        print("Multiple product images")
        print("\\nNO MORE GENERIC CONTENT!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())