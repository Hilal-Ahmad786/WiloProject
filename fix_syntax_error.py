#!/usr/bin/env python3
"""
Fix the syntax error in shopify_config.py caused by the previous regex replacement
"""

def fix_syntax_error():
    """Fix the broken string literal in shopify_config.py"""
    
    # Read the broken file
    try:
        with open('gui/widgets/shopify_config.py', 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Could not read shopify_config.py: {e}")
        return False
    
    print("🔍 Checking for syntax errors around line 64...")
    
    # Show the content around line 64 to understand the issue
    lines = content.split('\n')
    if len(lines) > 64:
        print("Lines around the error:")
        for i in range(max(0, 60), min(len(lines), 70)):
            print(f"Line {i+1:2d}: {lines[i]}")
    
    # Look for common string literal issues
    issues_found = []
    
    # Check for unmatched quotes
    if "'''" in content and content.count("'''") % 2 != 0:
        issues_found.append("Unmatched triple quotes")
    
    if '"""' in content and content.count('"""') % 2 != 0:
        issues_found.append("Unmatched triple double quotes")
    
    # Look for the specific problem - likely a broken string in the validation method
    if "_is_valid_image_url" in content:
        print("✅ Found image validation method - checking for string issues...")
        
        # Find the validation method
        method_start = content.find("def _is_valid_image_url")
        if method_start != -1:
            method_end = content.find("\n    def ", method_start + 1)
            if method_end == -1:
                method_end = content.find("\nclass ", method_start + 1)
            if method_end == -1:
                method_end = len(content)
            
            method_content = content[method_start:method_end]
            
            # Look for broken strings in the method
            if "print(f\"🔍 Image URL validation:" in method_content:
                print("🔧 Found the broken string - fixing it...")
                
                # Fix the specific broken line
                broken_pattern = r"print\(f\"🔍 Image URL validation: \{url\[:80\]\}\.\.\. - \{'VALID' if has_valid_extension else 'INVALID'\}\"\)"
                fixed_line = 'print(f"🔍 Image URL validation: {url[:80]}... - {\'VALID\' if has_valid_extension else \'INVALID\'}")'
                
                content = content.replace(
                    'print(f"🔍 Image URL validation: {url[:80]}... - {\'VALID\' if has_valid_extension else \'INVALID\'}")',
                    'print(f"🔍 Image URL validation: {url[:80]}... - VALID" if has_valid_extension else f"🔍 Image URL validation: {url[:80]}... - INVALID")'
                )
    
    # Alternative approach - if we can't fix it precisely, recreate a simpler version
    if issues_found or "SyntaxError" in str(content):
        print("🔧 Rebuilding the validation method with simpler syntax...")
        
        # Create a simple, clean validation method
        simple_validation = '''
    def _is_valid_image_url(self, url):
        """Validate image URL for Shopify compatibility"""
        try:
            if not url or not isinstance(url, str):
                return False
            
            url = url.strip()
            
            if not url.startswith(('http://', 'https://')):
                return False
            
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
            url_lower = url.lower()
            has_valid_extension = any(ext in url_lower for ext in valid_extensions)
            
            invalid_patterns = ['javascript:', 'data:', 'blob:', 'file:', '#', '<', '>', '"', "'"]
            for pattern in invalid_patterns:
                if pattern in url:
                    return False
            
            if len(url) > 2048:
                return False
            
            return has_valid_extension
            
        except Exception:
            return False'''
        
        # Remove the broken validation method if it exists
        import re
        pattern = r'\n    def _is_valid_image_url\(self, url\):.*?(?=\n    def |\nclass |\Z)'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Find a good place to add the simple validation method
        create_product_pos = content.find('def create_product(self, product_data):')
        if create_product_pos > 0:
            # Insert before create_product method
            content = content[:create_product_pos] + simple_validation + '\n\n    ' + content[create_product_pos:]
        
        # Also fix the image handling to use simpler validation
        image_handling_fix = '''
            # Add images with simple validation
            images = []
            card_image = product_data.get('card_image_url', '')
            product_images = product_data.get('product_images', [])
            
            if card_image and self._is_valid_image_url(card_image):
                images.append({
                    'src': card_image,
                    'alt': f"{name} - Card Image"
                })
                print("🖼️ Added card image")
            
            for i, img_url in enumerate(product_images[:5]):
                if img_url and self._is_valid_image_url(img_url):
                    if img_url not in [img['src'] for img in images]:
                        images.append({
                            'src': img_url,
                            'alt': f"{name} - Image {i+1}"
                        })
                        print(f"🖼️ Added product image {i+1}")
            
            if images:
                shopify_product['images'] = images'''
        
        # Replace any complex image handling with the simple version
        pattern = r'# Add images.*?print\(f"✅ Total validated images:.*?\)'
        content = re.sub(pattern, image_handling_fix, content, flags=re.DOTALL)
    
    # Write the fixed content
    try:
        with open('gui/widgets/shopify_config.py', 'w') as f:
            f.write(content)
        
        print("✅ Fixed syntax errors in shopify_config.py")
        return True
        
    except Exception as e:
        print(f"❌ Error writing fixed file: {e}")
        return False

def test_syntax():
    """Test if the Python file has valid syntax"""
    try:
        import ast
        with open('gui/widgets/shopify_config.py', 'r') as f:
            content = f.read()
        
        ast.parse(content)
        print("✅ Python syntax is now valid!")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error still exists: {e}")
        print(f"   Line {e.lineno}: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def main():
    """Fix the syntax error"""
    print("🔧 FIXING SYNTAX ERROR IN SHOPIFY_CONFIG.PY")
    print("=" * 50)
    
    print("The regex replacement broke a string literal.")
    print("Let me fix this and create a simpler validation method.")
    
    try:
        success = fix_syntax_error()
        
        if success:
            # Test the syntax
            syntax_ok = test_syntax()
            
            if syntax_ok:
                print("\n✅ SYNTAX ERROR FIXED!")
                print("\n🚀 Now you can test the complete workflow:")
                print("1. python main.py")
                print("2. Extract products")
                print("3. Upload to Shopify (with image validation)")
                
                print("\n🎯 The validation will:")
                print("• Check if image URLs are valid")
                print("• Skip invalid images instead of failing")
                print("• Upload products successfully even with some bad images")
                
            else:
                print("\n❌ Still have syntax issues - manual fix needed")
                print("Check gui/widgets/shopify_config.py around line 64")
        else:
            print("\n❌ Could not automatically fix the syntax error")
            
    except Exception as e:
        print(f"\n❌ Error during fix: {e}")
        
        print("\n🔧 MANUAL FIX NEEDED:")
        print("The automatic fix broke the Python syntax.")
        print("Please check gui/widgets/shopify_config.py around line 64")
        print("Look for unmatched quotes or broken strings.")

if __name__ == "__main__":
    main()