"""
Shopify API client
"""

import requests
from utils.logger import get_logger

class ShopifyClient:
    """Shopify API client"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.base_url = f"https://{settings.shopify_shop_url}/admin/api/2023-10"
        
    def test_connection(self):
        """Test Shopify API connection"""
        try:
            url = f"{self.base_url}/shop.json"
            headers = self.settings.get_shopify_headers()
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                shop_data = response.json()
                self.logger.info(f"Connected to shop: {shop_data['shop']['name']}")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
