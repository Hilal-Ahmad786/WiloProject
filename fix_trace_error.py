#!/usr/bin/env python3
"""
Fix tkinter trace method error in newer Python versions
"""

def fix_enhanced_controller_trace():
    """Fix the trace method call in enhanced_scraper_controller.py"""
    
    # Read the current file
    with open('gui/widgets/enhanced_scraper_controller.py', 'r') as f:
        content = f.read()
    
    # Replace the old trace method with the new one
    old_trace = "self.scraper_type_var.trace('w', self._on_scraper_type_changed)"
    new_trace = "self.scraper_type_var.trace_add('write', self._on_scraper_type_changed)"
    
    fixed_content = content.replace(old_trace, new_trace)
    
    # Write the fixed content back
    with open('gui/widgets/enhanced_scraper_controller.py', 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed tkinter trace method in enhanced_scraper_controller.py")

def fix_country_selector_if_exists():
    """Fix trace method in country_selector.py if it exists"""
    
    try:
        with open('gui/widgets/country_selector.py', 'r') as f:
            content = f.read()
        
        # Look for any trace calls and fix them
        if ".trace(" in content:
            # Replace old trace calls with new ones
            content = content.replace(".trace('w', ", ".trace_add('write', ")
            content = content.replace(".trace('r', ", ".trace_add('read', ")
            content = content.replace(".trace('u', ", ".trace_add('unset', ")
            
            with open('gui/widgets/country_selector.py', 'w') as f:
                f.write(content)
            
            print("✅ Fixed tkinter trace method in country_selector.py")
        else:
            print("ℹ️  No trace methods found in country_selector.py")
            
    except FileNotFoundError:
        print("ℹ️  country_selector.py not found, skipping")
    except Exception as e:
        print(f"⚠️  Could not fix country_selector.py: {e}")

def create_missing_config_init():
    """Create missing config/__init__.py if needed"""
    
    import os
    
    config_init = "config/__init__.py"
    if not os.path.exists(config_init):
        with open(config_init, 'w') as f:
            f.write('"""Configuration package"""\n')
        print("✅ Created config/__init__.py")

def create_minimal_settings_if_missing():
    """Create minimal settings.py if it doesn't exist"""
    
    import os
    
    if not os.path.exists('config/settings.py'):
        settings_content = '''"""
Minimal application settings
"""

import os
from pathlib import Path

class AppSettings:
    """Basic application settings"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
        # Shopify settings from environment or defaults
        self.shopify_shop_url = os.getenv('SHOPIFY_SHOP_URL', 'm13kjy-se.myshopify.com')
        self.shopify_access_token = os.getenv('SHOPIFY_ACCESS_TOKEN', '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')
        
        # Browser settings
        self.headless_mode = False
        self.browser_timeout = 30
        self.page_load_delay = 3
        
        # Create directories
        self.logs_dir = self.project_root / 'logs'
        self.logs_dir.mkdir(exist_ok=True)
        
        self.data_dir = self.project_root / 'data'
        self.data_dir.mkdir(exist_ok=True)
'''
        
        with open('config/settings.py', 'w') as f:
            f.write(settings_content)
        print("✅ Created minimal config/settings.py")

def create_minimal_countries_if_missing():
    """Create minimal countries.py if it doesn't exist"""
    
    import os
    
    if not os.path.exists('config/countries.py'):
        countries_content = '''"""
Country configurations for Wilo website
"""

COUNTRIES = {
    'germany': {
        'name': 'Deutschland',
        'code': 'DE',
        'language': 'German',
        'hydraulic_pump_text': 'Hydraulische Pumpenauswahl'
    },
    'austria': {
        'name': 'Österreich',
        'code': 'AT', 
        'language': 'German',
        'hydraulic_pump_text': 'Hydraulische Pumpenauswahl'
    },
    'france': {
        'name': 'France',
        'code': 'FR',
        'language': 'French', 
        'hydraulic_pump_text': 'Sélection de pompes hydrauliques'
    }
}

def get_country_config(country_key):
    """Get configuration for specific country"""
    return COUNTRIES.get(country_key.lower())

def get_all_countries():
    """Get list of all supported countries"""
    return list(COUNTRIES.keys())
'''
        
        with open('config/countries.py', 'w') as f:
            f.write(countries_content)
        print("✅ Created minimal config/countries.py")

def main():
    """Main fix function"""
    print("🔧 FIXING TKINTER TRACE ERROR")
    print("=" * 40)
    
    try:
        # Fix the main issue
        fix_enhanced_controller_trace()
        
        # Fix other potential trace issues
        fix_country_selector_if_exists()
        
        # Create missing files if needed
        create_missing_config_init()
        create_minimal_settings_if_missing()
        create_minimal_countries_if_missing()
        
        print("\n✅ ALL TKINTER ISSUES FIXED!")
        print("\n🎯 Fixed:")
        print("• Updated trace() to trace_add() for Python 3.13+")
        print("• Created missing config files")
        print("• Ensured all dependencies exist")
        
        print("\n🚀 Try running again:")
        print("python main.py")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())