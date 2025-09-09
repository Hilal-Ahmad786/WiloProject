#!/usr/bin/env python3
"""
Fix the indentation error in wilo_scraper.py
"""

def fix_indentation_error():
    """Fix the indentation error around line 710-711"""
    
    with open('scraper/wilo_scraper.py', 'r') as f:
        lines = f.readlines()
    
    # Find the problematic area around line 710
    for i, line in enumerate(lines):
        if "if image_info['sprite_sheet_url']:" in line:
            # Fix the indentation for the if-else block
            lines[i] = "                            if image_info['sprite_sheet_url']:\n"
            if i + 1 < len(lines):
                lines[i + 1] = "                                self.logger.info(f\"✅ SPRITE IMAGE found for {product_name}: Position {image_info['sprite_position']}\")\n"
            if i + 2 < len(lines):
                lines[i + 2] = "                            elif image_info['image_url']:\n"
            if i + 3 < len(lines):
                lines[i + 3] = "                                self.logger.info(f\"✅ DIRECT IMAGE found for {product_name}: {image_info['image_url']}\")\n"
            if i + 4 < len(lines):
                lines[i + 4] = "                            else:\n"
            if i + 5 < len(lines):
                lines[i + 5] = "                                self.logger.warning(f\"❌ NO IMAGE found for {product_name}\")\n"
            break
    
    # Write the fixed content
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Fixed indentation error!")

def alternative_fix():
    """Alternative approach - replace the problematic logging section"""
    
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # Find and replace the problematic logging section
    old_logging = '''if image_info['sprite_sheet_url']:
                                self.logger.info(f"✅ SPRITE IMAGE found for {product_name}: Position {image_info['sprite_position']}")
                            elif image_info['image_url']:
                                self.logger.info(f"✅ DIRECT IMAGE found for {product_name}: {image_info['image_url']}")
                            else:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")'''
    
    new_logging = '''                            if image_info.get('sprite_sheet_url'):
                                self.logger.info(f"✅ SPRITE IMAGE found for {product_name}: Position {image_info['sprite_position']}")
                            elif image_info.get('image_url'):
                                self.logger.info(f"✅ DIRECT IMAGE found for {product_name}: {image_info['image_url']}")
                            else:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")'''
    
    if old_logging in content:
        content = content.replace(old_logging, new_logging)
        print("✅ Fixed logging with alternative approach!")
    else:
        # If exact match not found, do a simpler fix
        content = content.replace(
            "if image_info['sprite_sheet_url']:",
            "                            if image_info.get('sprite_sheet_url'):"
        )
        print("✅ Applied simple indentation fix!")
    
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(content)

def main():
    print("🔧 Fixing Indentation Error in wilo_scraper.py")
    print("=" * 45)
    
    try:
        alternative_fix()
        print("\n✅ Indentation error should be fixed!")
        print("\n🚀 Try running again:")
        print("python main.py")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        print("\nFallback: You can manually fix line 710-711 in scraper/wilo_scraper.py")
        print("Make sure the if-else block is properly indented.")

if __name__ == "__main__":
    main()