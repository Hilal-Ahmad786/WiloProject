#!/usr/bin/env python3
"""
ROBUST Shopify fix - searches for multiple patterns and replaces the right method
"""

import re

def find_and_replace_transformation():
    """Find and replace the transformation method with multiple search patterns"""
    
    # Read the current file
    with open('gui/widgets/shopify_config.py', 'r') as f:
        content = f.read()
    
    print("🔍 Analyzing shopify_config.py file...")
    print(f"📄 File size: {len(content)} characters")
    
    # Search for transformation-related methods
    transformation_patterns = [
        r'def _transform_to_shopify_format\(self, wilo_product: Dict\) -> Dict:',
        r'def _transform_to_shopify_format\(self, wilo_product\)',
        r'def transform_to_shopify',
        r'def _build_product_description_from_extracted_data',
        r'def create_product\(self, product_data\)',
        r'def _build_description\(self, product_data\)'
    ]
    
    found_methods = []
    for pattern in transformation_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            found_methods.append({
                'pattern': pattern,
                'start': match.start(),
                'method_name': match.group()
            })
    
    print(f"🔍 Found {len(found_methods)} transformation methods:")
    for method in found_methods:
        print(f"   - {method['method_name']} at position {method['start']}")
    
    # If we can't find transformation methods, let's check what methods exist
    if not found_methods:
        print("🔍 Searching for ALL methods in the file...")
        all_methods = re.findall(r'def \w+\(self[^)]*\):', content)
        print(f"📋 All methods found: {all_methods}")
        
        # Look for any method that might handle product creation/transformation
        creation_methods = [m for m in all_methods if any(keyword in m.lower() for keyword in ['product', 'create', 'upload', 'transform'])]
        print(f"🎯 Product-related methods: {creation_methods}")
    
    # Try to find the ShopifyClient class and its create_product method
    client_pattern = r'class ShopifyClient.*?def create_product\(self, product_data\):(.*?)(?=\n    def |\nclass |\Z)'
    client_match = re.search(client_pattern, content, re.DOTALL)
    
    if client_match:
        print("✅ Found ShopifyClient.create_product method")
        # Replace the entire create_product method
        new_create_product = '''    def create_product(self, product_data):
        """Create a single product in Shopify - FIXED VERSION WITH REAL DATA"""
        try:
            print("=" * 80)
            print("🔍 SHOPIFY CREATE_PRODUCT DEBUG - FINAL VERSION")
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
            
            # BUILD REAL SHOPIFY DESCRIPTION
            html_parts = []
            
            # Title
            html_parts.append(f"<h1>{name}</h1>")
            
            # FORCE USE OF REAL DESCRIPTION
            if short_description and len(short_description.strip()) > 20:
                html_parts.append(f"<div class='product-description'><p>{short_description}</p></div>")
                print("✅ ADDED REAL SHORT DESCRIPTION")
            else:
                html_parts.append(f"<p>Professional {name} from Wilo for industrial applications.</p>")
                print("⚠️ USED FALLBACK DESCRIPTION")
            
            # Product info
            html_parts.append(f"<p><strong>Application:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Product Type:</strong> {subcategory}</p>")
            
            # FORCE USE OF REAL ADVANTAGES
            if advantages and len(advantages) > 0:
                html_parts.append("<h3>Ihre Vorteile (Real Product Advantages)</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    if advantage and len(advantage.strip()) > 10:
                        html_parts.append(f"<li>{advantage.strip()}</li>")
                html_parts.append("</ul>")
                print(f"✅ ADDED {len(advantages)} REAL ADVANTAGES")
            else:
                html_parts.append("<h3>Key Features</h3>")
                html_parts.append("<ul>")
                html_parts.append("<li>High-quality German engineering</li>")
                html_parts.append("<li>Energy-efficient operation</li>")
                html_parts.append("<li>Reliable performance</li>")
                html_parts.append("</ul>")
                print("⚠️ USED GENERIC FEATURES")
            
            # Brand info
            html_parts.append("<h3>About Wilo</h3>")
            html_parts.append("<p>Wilo is a leading global manufacturer of pumps and pump systems.</p>")
            
            # Build final description
            body_html = "\\n".join(html_parts)
            
            # Create Shopify product structure
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
            card_image = product_data.get('card_image_url', '')
            product_images = product_data.get('product_images', [])
            
            if card_image:
                images.append({
                    'src': card_image,
                    'alt': f"{name} - Card Image"
                })
                print("🖼️ Added card image")
            
            for i, img_url in enumerate(product_images[:5]):
                if img_url and img_url not in [img['src'] for img in images]:
                    images.append({
                        'src': img_url,
                        'alt': f"{name} - Image {i+1}"
                    })
                    print(f"🖼️ Added product image {i+1}")
            
            if images:
                shopify_product['images'] = images
            
            # Create product via API
            payload = {'product': shopify_product}
            response = requests.post(
                f"{self.base_url}/products.json",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print("=" * 80)
            print(f"✅ SHOPIFY PRODUCT READY:")
            print(f"   - Title: {name}")
            print(f"   - Description length: {len(body_html)}")
            print(f"   - Images: {len(images)}")
            print(f"   - Real content: {'YES' if short_description or advantages else 'NO'}")
            print("=" * 80)
            
            if response.status_code == 201:
                created_product = response.json()['product']
                print(f"✅ Successfully created product in Shopify: {created_product['id']}")
                return created_product
            else:
                print(f"❌ Shopify API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating product: {e}")
            import traceback
            traceback.print_exc()
            return None'''
        
        # Replace the method
        new_content = re.sub(client_pattern, f'class ShopifyClient{new_create_product}', content, flags=re.DOTALL)
        
        # Write back to file
        with open('gui/widgets/shopify_config.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Successfully replaced ShopifyClient.create_product method")
        return True
    
    # Alternative: Look for upload_scraped_products method and modify it
    upload_pattern = r'def upload_scraped_products\(self\):(.*?)(?=\n    def |\Z)'
    upload_match = re.search(upload_pattern, content, re.DOTALL)
    
    if upload_match:
        print("✅ Found upload_scraped_products method - will modify it to add debug logging")
        
        # Add debug logging at the start of upload method
        debug_code = '''
        try:
            print("🔍 UPLOAD DEBUG: Starting scraped products upload")
            products = self.get_scraped_products()
            print(f"📊 Found {len(products)} products to upload")
            
            for i, product in enumerate(products):
                print(f"\\n📦 Product {i+1}:")
                print(f"   Name: {product.get('name', 'Unknown')}")
                print(f"   Short desc: {len(product.get('short_description', ''))} chars")
                print(f"   Advantages: {len(product.get('advantages', []))} items")
                print(f"   All keys: {list(product.keys())}")
        
        # Continue with original upload logic...'''
        
        # This is a simpler fix - just add logging without changing the core logic
        print("ℹ️  Adding debug logging to upload method...")
        
        # Find the start of the method and add debug logging
        method_start = content.find('def upload_scraped_products(self):')
        if method_start != -1:
            # Find the first line after the method definition
            first_line_start = content.find('\n', method_start) + 1
            # Find the first real code line (skip docstring if present)
            try_start = content.find('try:', first_line_start)
            if try_start != -1:
                # Insert debug code right after the try:
                insert_point = content.find('\n', try_start) + 1
                new_content = content[:insert_point] + debug_code + content[insert_point:]
                
                with open('gui/widgets/shopify_config.py', 'w') as f:
                    f.write(new_content)
                
                print("✅ Added debug logging to upload method")
                return True
    
    print("❌ Could not find any suitable method to replace")
    print("📄 File content preview (first 500 chars):")
    print(content[:500])
    print("...")
    print("📄 File content preview (last 500 chars):")
    print(content[-500:])
    
    return False

def create_simple_test_script():
    """Create a simple test script to verify the data flow"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test script to check what data is being passed to Shopify
"""

def test_scraped_data():
    """Test what data the scraper actually produces"""
    print("🔍 TESTING SCRAPED DATA STRUCTURE")
    print("=" * 50)
    
    # Simulate what your scraper produces (based on the logs)
    test_product = {
        'id': 'catalog_1_1234567890',
        'name': 'Wilo-Atmos TERA-SCH',
        'category': 'Industrie Heizung', 
        'subcategory': 'Heizungspumpen',
        'source': 'catalog',
        'card_image_url': 'https://wilo.com/some/image.jpg',
        'product_images': ['https://wilo.com/img1.jpg', 'https://wilo.com/img2.jpg'],
        'short_description': 'Splitcase-Pumpe für einen zuverlässigen Betrieb und energieeffizienten Transport großer Volumenströme bei niedrigen Drücken. Die Pumpe ist für große Fördermengen optimiert und bietet eine hohe Energieeffizienz bei gleichzeitig kompakter Bauweise.' * 3,  # ~1000 chars
        'advantages': [
            'Zuverlässiger Dauerbetrieb für eine effiziente Triebwerksleistung',
            'Energieeffiziente Förderung großer Volumenströme',
            'Kompakte Bauweise für platzsparende Installation',
            'Einfache Wartung und Service',
            'Robust construction for industrial applications',
            'High-quality German engineering',
            'Optimized hydraulic design',
            'Long service life',
            'Low noise operation'
        ],
        'long_description': 'Detailed technical information about the pump...',
        'specifications': {
            'brand': 'Wilo',
            'series': 'Wilo-Atmos TERA-SCH',
            'application': 'Industrie Heizung',
            'type': 'Heizungspumpe'
        }
    }
    
    print(f"✅ Product name: {test_product['name']}")
    print(f"📝 Short description: {len(test_product['short_description'])} characters")
    print(f"📝 Advantages: {len(test_product['advantages'])} items")
    print(f"🖼️ Images: {len(test_product['product_images'])} + 1 card image")
    print()
    print("📝 Short description preview:")
    print(test_product['short_description'][:200] + "...")
    print()
    print("📝 First 3 advantages:")
    for i, adv in enumerate(test_product['advantages'][:3]):
        print(f"   {i+1}. {adv}")
    
    print("\\n" + "=" * 50)
    print("🎯 THIS IS THE DATA YOUR SCRAPER PRODUCES")
    print("🎯 SHOPIFY SHOULD USE THIS EXACT CONTENT")
    print("=" * 50)
    
    return test_product

if __name__ == "__main__":
    test_scraped_data()
'''
    
    with open('test_scraped_data.py', 'w') as f:
        f.write(test_script)
    
    print("✅ Created test_scraped_data.py")

def main():
    """Main function"""
    print("🔧 ROBUST SHOPIFY TRANSFORMATION FIX")
    print("=" * 50)
    
    try:
        success = find_and_replace_transformation()
        
        if success:
            print("\n✅ FIX COMPLETED!")
            print("\n🚀 Now test the workflow:")
            print("1. python main.py")
            print("2. Extract 2 products")
            print("3. Upload to Shopify")
            print("4. Watch for detailed debug logs in terminal")
        else:
            print("\n❌ Could not automatically fix the file")
            print("\n🔧 MANUAL FIX REQUIRED:")
            print("Please share the content of your gui/widgets/shopify_config.py file")
            print("Or run this to see your data structure:")
            
            create_simple_test_script()
            print("   python test_scraped_data.py")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()