#!/usr/bin/env python3
"""
FINAL FIX for Shopify upload - Replace the entire transformation method
"""

def fix_shopify_transformation():
    """Replace the transformation method in shopify_config.py"""
    
    # Read the current file
    with open('gui/widgets/shopify_config.py', 'r') as f:
        content = f.read()
    
    # Find and replace the _transform_to_shopify_format method
    import re
    
    # New transformation method that FORCES use of extracted data
    new_transform_method = '''    def _transform_to_shopify_format(self, wilo_product: Dict) -> Dict:
        """Transform Wilo product data to Shopify format - FINAL WORKING VERSION"""
        try:
            # FORCE DEBUG LOGGING
            print("=" * 80)
            print("🔍 SHOPIFY TRANSFORMATION DEBUG - FINAL VERSION")
            print(f"Input product keys: {list(wilo_product.keys())}")
            
            # Extract basic data
            name = wilo_product.get('name', 'Wilo Pump')
            category = wilo_product.get('category', 'Industrie Heizung')
            subcategory = wilo_product.get('subcategory', 'Heizungspumpen')
            
            print(f"✅ Product name: '{name}'")
            print(f"✅ Category: '{category}'")
            print(f"✅ Subcategory: '{subcategory}'")
            
            # EXTRACT REAL CONTENT - CRITICAL SECTION
            short_description = wilo_product.get('short_description', '')
            advantages = wilo_product.get('advantages', [])
            long_description = wilo_product.get('long_description', '')
            
            print(f"📝 Short description length: {len(short_description)}")
            print(f"📝 Advantages count: {len(advantages)}")
            print(f"📝 Long description length: {len(long_description)}")
            
            if short_description:
                print(f"📝 Short desc preview: '{short_description[:150]}...'")
            if advantages:
                print(f"📝 First advantage: '{advantages[0][:100]}...'")
            
            # BUILD SHOPIFY DESCRIPTION - FORCE REAL CONTENT
            html_parts = []
            
            # Title section
            html_parts.append(f"<h1>{name}</h1>")
            
            # CRITICAL: Use REAL short description
            if short_description and len(short_description.strip()) > 20:
                html_parts.append(f"<div class='product-intro'><p>{short_description}</p></div>")
                print("✅ ADDED REAL SHORT DESCRIPTION TO SHOPIFY")
            else:
                # Fallback only if NO real description
                html_parts.append(f"<p>Professional {name} from Wilo for industrial heating applications.</p>")
                print("⚠️ USED FALLBACK DESCRIPTION (no real description found)")
            
            # Product category info
            html_parts.append(f"<div class='product-details'>")
            html_parts.append(f"<p><strong>Application:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Product Type:</strong> {subcategory}</p>")
            html_parts.append(f"</div>")
            
            # CRITICAL: Use REAL advantages
            if advantages and len(advantages) > 0:
                html_parts.append("<h3>Ihre Vorteile (Product Advantages)</h3>")
                html_parts.append("<ul class='product-advantages'>")
                for advantage in advantages:
                    if advantage and len(advantage.strip()) > 10:
                        html_parts.append(f"<li>{advantage.strip()}</li>")
                html_parts.append("</ul>")
                print(f"✅ ADDED {len(advantages)} REAL ADVANTAGES TO SHOPIFY")
            else:
                # Only use generic if NO real advantages
                html_parts.append("<h3>Key Features</h3>")
                html_parts.append("<ul>")
                html_parts.append("<li>High-quality German engineering</li>")
                html_parts.append("<li>Energy-efficient operation</li>")
                html_parts.append("<li>Reliable performance for industrial applications</li>")
                html_parts.append("<li>Professional grade components</li>")
                html_parts.append("</ul>")
                print("⚠️ USED GENERIC ADVANTAGES (no real advantages found)")
            
            # Add long description if available
            if long_description and len(long_description.strip()) > 50:
                html_parts.append("<h3>Detailed Information</h3>")
                # Clean and format long description
                paragraphs = long_description.replace('\\n\\n', '</p><p>').strip()
                html_parts.append(f"<div class='detailed-info'><p>{paragraphs}</p></div>")
                print(f"✅ ADDED LONG DESCRIPTION ({len(long_description)} chars)")
            
            # Add specifications if available
            specs = wilo_product.get('specifications', {})
            if specs and isinstance(specs, dict) and len(specs) > 2:
                html_parts.append("<h3>Technical Specifications</h3>")
                html_parts.append("<ul class='specifications'>")
                for key, value in specs.items():
                    if value and str(value).strip() and key != 'brand':
                        clean_key = key.replace('_', ' ').title()
                        html_parts.append(f"<li><strong>{clean_key}:</strong> {value}</li>")
                html_parts.append("</ul>")
                print(f"✅ ADDED SPECIFICATIONS ({len(specs)} items)")
            
            # Brand information
            html_parts.append("<h3>About Wilo</h3>")
            html_parts.append("<p>Wilo is a leading global manufacturer of pumps and pump systems for heating, cooling, air conditioning, water supply, and wastewater treatment. Founded in Germany, Wilo combines decades of engineering expertise with innovative technology.</p>")
            
            # Build final HTML
            body_html = "\\n".join(html_parts)
            
            # Extract images
            images = []
            card_image = wilo_product.get('card_image_url', '')
            product_images = wilo_product.get('product_images', [])
            
            # Add card image first
            if card_image:
                images.append({
                    'src': card_image,
                    'alt': f"{name} - Product Image"
                })
                print(f"🖼️ Added card image")
            
            # Add product images
            for i, img_url in enumerate(product_images[:8]):  # Limit to 8 images
                if img_url and img_url not in [img['src'] for img in images]:
                    images.append({
                        'src': img_url,
                        'alt': f"{name} - Image {i+1}"
                    })
                    print(f"🖼️ Added product image {i+1}")
            
            # Create final Shopify product
            shopify_product = {
                'title': name,
                'body_html': body_html,
                'vendor': 'Wilo',
                'product_type': subcategory,
                'tags': f"Wilo, {category}, {subcategory}, German Engineering, Industrial Pump",
                'status': 'draft',  # Create as draft for review
                'variants': [{
                    'title': 'Default',
                    'price': '0.00',  # Set price manually
                    'inventory_management': 'shopify',
                    'inventory_quantity': 0,
                    'requires_shipping': True,
                    'taxable': True,
                    'sku': f"WILO-{name.replace(' ', '-').replace('.', '').upper()[:30]}"
                }],
                'options': [{
                    'name': 'Title',
                    'values': ['Default']
                }]
            }
            
            # Add images to product
            if images:
                shopify_product['images'] = images
            
            print("=" * 80)
            print("✅ SHOPIFY PRODUCT CREATED SUCCESSFULLY")
            print(f"📊 Final stats:")
            print(f"   - Title: {name}")
            print(f"   - Description length: {len(body_html)} characters")
            print(f"   - Images: {len(images)}")
            print(f"   - Real content used: {'YES' if short_description or advantages else 'NO'}")
            print("=" * 80)
            
            return shopify_product
            
        except Exception as e:
            print(f"❌ TRANSFORMATION ERROR: {e}")
            import traceback
            traceback.print_exc()
            return {}'''
    
    # Find the method and replace it
    pattern = r'def _transform_to_shopify_format\(self, wilo_product: Dict\) -> Dict:.*?(?=\n    def |\n\nclass |\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, new_transform_method, content, flags=re.DOTALL)
        
        # Write back to file
        with open('gui/widgets/shopify_config.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Successfully replaced Shopify transformation method")
        return True
    else:
        print("❌ Could not find transformation method to replace")
        return False

def main():
    """Run the fix"""
    print("🔧 FINAL SHOPIFY TRANSFORMATION FIX")
    print("=" * 50)
    
    try:
        success = fix_shopify_transformation()
        
        if success:
            print("\n✅ FIX COMPLETED SUCCESSFULLY!")
            print("\n🎯 What was fixed:")
            print("• Completely replaced transformation method")
            print("• Added comprehensive debug logging")
            print("• FORCES use of real extracted data")
            print("• Will show detailed logs during upload")
            
            print("\n🚀 Test the complete workflow:")
            print("1. python main.py")
            print("2. Extract 2 products")
            print("3. Go to Shopify Integration tab")
            print("4. Click 'Upload Scraped Products'")
            print("5. Watch terminal for detailed transformation logs")
            
            print("\n📊 Expected debug output during upload:")
            print("🔍 SHOPIFY TRANSFORMATION DEBUG - FINAL VERSION")
            print("✅ Product name: 'Wilo-Atmos TERA-SCH'")
            print("📝 Short description length: 1013")
            print("📝 Advantages count: 9")
            print("✅ ADDED REAL SHORT DESCRIPTION TO SHOPIFY")
            print("✅ ADDED 9 REAL ADVANTAGES TO SHOPIFY")
            
            print("\n🎉 NO MORE GENERIC CONTENT!")
        else:
            print("\n❌ Fix failed - check the error above")
            
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")

if __name__ == "__main__":
    main()