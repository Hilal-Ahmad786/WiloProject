"""
Enhanced Shopify API client with product upload functionality
"""

import requests
import json
import time
from typing import List, Dict, Optional
from utils.logger import get_logger

class ShopifyClient:
    """Enhanced Shopify API client for product management"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Build API URL
        shop_url = settings.shopify_shop_url
        if not shop_url.startswith('http'):
            if not shop_url.endswith('.myshopify.com'):
                shop_url = f"{shop_url}.myshopify.com"
            shop_url = f"https://{shop_url}"
        
        self.base_url = f"{shop_url}/admin/api/2024-01"
        self.headers = {
            'X-Shopify-Access-Token': settings.shopify_access_token,
            'Content-Type': 'application/json'
        }
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 500ms between requests
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make rate-limited API request"""
        try:
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last)
            
            url = f"{self.base_url}/{endpoint}"
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            self.last_request_time = time.time()
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 2))
                self.logger.warning(f"Rate limited, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, data)
            
            if response.status_code >= 400:
                self.logger.error(f"API error {response.status_code}: {response.text}")
                return None
            
            return response.json() if response.text else {}
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Shopify API connection"""
        try:
            response = self._make_request('GET', 'shop.json')
            
            if response and 'shop' in response:
                shop_data = response['shop']
                self.logger.info(f"✅ Connected to Shopify store: {shop_data.get('name', 'Unknown')}")
                self.logger.info(f"Store URL: {shop_data.get('domain', 'Unknown')}")
                self.logger.info(f"Store ID: {shop_data.get('id', 'Unknown')}")
                return True
            else:
                self.logger.error("❌ Failed to connect to Shopify")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Connection test failed: {e}")
            return False
    
    def create_product(self, product_data: Dict) -> Optional[Dict]:
        """Create a single product in Shopify"""
        try:
            # Transform Wilo product data to Shopify format
            shopify_product = self._transform_to_shopify_format(product_data)
            
            payload = {'product': shopify_product}
            response = self._make_request('POST', 'products.json', payload)
            
            if response and 'product' in response:
                created_product = response['product']
                self.logger.info(f"✅ Created product: {created_product.get('title', 'Unknown')} (ID: {created_product.get('id')})")
                return created_product
            else:
                self.logger.error(f"❌ Failed to create product: {product_data.get('name', 'Unknown')}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error creating product: {e}")
            return None
    
    def bulk_upload_products(self, products: List[Dict], progress_callback=None) -> Dict:
        """Upload multiple products to Shopify with progress tracking"""
        results = {
            'successful': [],
            'failed': [],
            'total': len(products),
            'success_count': 0,
            'error_count': 0
        }
        
        try:
            self.logger.info(f"Starting bulk upload of {len(products)} products...")
            
            for i, product in enumerate(products):
                try:
                    if progress_callback:
                        progress_callback(f"Uploading product {i+1}/{len(products)}: {product.get('name', 'Unknown')}")
                    
                    # Check if product already exists
                    existing = self._find_existing_product(product)
                    if existing:
                        self.logger.info(f"⏭️  Product already exists: {product.get('name', 'Unknown')}")
                        results['successful'].append({
                            'product': product,
                            'shopify_id': existing['id'],
                            'action': 'skipped',
                            'reason': 'already_exists'
                        })
                        results['success_count'] += 1
                        continue
                    
                    # Create new product
                    created_product = self.create_product(product)
                    
                    if created_product:
                        results['successful'].append({
                            'product': product,
                            'shopify_id': created_product['id'],
                            'action': 'created'
                        })
                        results['success_count'] += 1
                    else:
                        results['failed'].append({
                            'product': product,
                            'error': 'Creation failed'
                        })
                        results['error_count'] += 1
                    
                    # Small delay between uploads
                    time.sleep(0.5)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing product {product.get('name', 'Unknown')}: {e}")
                    results['failed'].append({
                        'product': product,
                        'error': str(e)
                    })
                    results['error_count'] += 1
            
            # Final summary
            self.logger.info(f"✅ Bulk upload completed!")
            self.logger.info(f"   Successful: {results['success_count']}")
            self.logger.info(f"   Failed: {results['error_count']}")
            self.logger.info(f"   Total: {results['total']}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Bulk upload failed: {e}")
            results['failed'] = products
            results['error_count'] = len(products)
            return results
    
    def _find_existing_product(self, product_data: Dict) -> Optional[Dict]:
        """Check if product already exists in Shopify"""
        try:
            # Search by product title
            title = product_data.get('name', '')
            if not title:
                return None
            
            # Use Shopify's product search
            response = self._make_request('GET', f'products.json?title={requests.utils.quote(title)}&limit=1')
            
            if response and 'products' in response and response['products']:
                return response['products'][0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking existing product: {e}")
            return None
    
    def _transform_to_shopify_format(self, wilo_product: Dict) -> Dict:
        """Transform Wilo product data to Shopify product format"""
        try:
            # Extract basic info
            name = wilo_product.get('name', 'Wilo Pump')
            category = wilo_product.get('category', 'Pumps')
            subcategory = wilo_product.get('subcategory', 'Standard')
            description = wilo_product.get('description', '')
            specifications = wilo_product.get('specifications', {})
            
            # Build enhanced description
            full_description = self._build_product_description(wilo_product)
            
            # Create Shopify product
            shopify_product = {
                'title': name,
                'body_html': full_description,
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
            
            # Add product image if available
            image_url = wilo_product.get('image_url', '')
            if image_url:
                shopify_product['images'] = [{
                    'src': image_url,
                    'alt': name
                }]
            
            # Add custom fields as metafields
            metafields = self._create_metafields(wilo_product)
            if metafields:
                shopify_product['metafields'] = metafields
            
            return shopify_product
            
        except Exception as e:
            self.logger.error(f"Error transforming product data: {e}")
            return {}
    
    def _build_product_description(self, product: Dict) -> str:
        """Build comprehensive product description"""
        try:
            name = product.get('name', 'Wilo Pump')
            category = product.get('category', 'Pumps')
            subcategory = product.get('subcategory', 'Standard')
            description = product.get('description', '')
            specs = product.get('specifications', {})
            
            html_parts = []
            
            # Header
            html_parts.append(f"<h2>{name}</h2>")
            
            # Basic description
            if description:
                html_parts.append(f"<p>{description}</p>")
            
            # Category information
            html_parts.append(f"<p><strong>Application:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Type:</strong> {subcategory}</p>")
            
            # Specifications
            if specs:
                html_parts.append("<h3>Specifications</h3>")
                html_parts.append("<ul>")
                for key, value in specs.items():
                    if value and str(value).strip():
                        html_parts.append(f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>")
                html_parts.append("</ul>")
            
            # Features
            html_parts.append("<h3>Features</h3>")
            html_parts.append("<ul>")
            html_parts.append("<li>High-quality German engineering</li>")
            html_parts.append("<li>Energy-efficient operation</li>")
            html_parts.append("<li>Reliable performance</li>")
            html_parts.append("<li>Professional grade components</li>")
            html_parts.append("</ul>")
            
            # Brand info
            html_parts.append("<h3>About Wilo</h3>")
            html_parts.append("<p>Wilo is a leading global manufacturer of pumps and pump systems for heating, cooling, air conditioning, water supply, and wastewater treatment.</p>")
            
            return "\n".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Error building description: {e}")
            return product.get('description', '')
    
    def _generate_tags(self, product: Dict) -> str:
        """Generate product tags for better organization"""
        tags = []
        
        # Add basic tags
        tags.append('Wilo')
        tags.append('Pump')
        tags.append('German Engineering')
        
        # Add category tags
        category = product.get('category', '')
        if category:
            tags.append(category.replace('.', '').strip())
        
        # Add subcategory tags
        subcategory = product.get('subcategory', '')
        if subcategory:
            tags.append(subcategory)
        
        # Add specification-based tags
        specs = product.get('specifications', {})
        if 'application' in specs:
            tags.append(specs['application'])
        
        return ', '.join(tags)
    
    def _generate_sku(self, product: Dict) -> str:
        """Generate SKU for the product"""
        try:
            # Extract parts for SKU
            name = product.get('name', 'WILO').upper().replace(' ', '-')
            category_num = product.get('category', '01. Unknown').split('.')[0].strip()
            
            # Create SKU: WILO-CATEGORY-PRODUCTNAME
            sku = f"WILO-{category_num}-{name}"
            
            # Clean up SKU (remove special characters)
            sku = ''.join(c for c in sku if c.isalnum() or c in '-_')
            
            return sku[:50]  # Limit length
            
        except Exception as e:
            self.logger.error(f"Error generating SKU: {e}")
            return f"WILO-{int(time.time())}"
    
    def _create_metafields(self, product: Dict) -> List[Dict]:
        """Create metafields for additional product data"""
        metafields = []
        
        try:
            # Add category as metafield
            if product.get('category'):
                metafields.append({
                    'namespace': 'wilo',
                    'key': 'category',
                    'value': product['category'],
                    'type': 'single_line_text_field'
                })
            
            # Add subcategory as metafield
            if product.get('subcategory'):
                metafields.append({
                    'namespace': 'wilo',
                    'key': 'subcategory',
                    'value': product['subcategory'],
                    'type': 'single_line_text_field'
                })
            
            # Add extraction info
            if product.get('extracted_at'):
                metafields.append({
                    'namespace': 'wilo',
                    'key': 'extracted_at',
                    'value': product['extracted_at'],
                    'type': 'date_time'
                })
            
            # Add source URL
            if product.get('source_url'):
                metafields.append({
                    'namespace': 'wilo',
                    'key': 'source_url',
                    'value': product['source_url'],
                    'type': 'url'
                })
            
            return metafields
            
        except Exception as e:
            self.logger.error(f"Error creating metafields: {e}")
            return []
    
    def get_products(self, limit: int = 50) -> List[Dict]:
        """Get existing products from Shopify"""
        try:
            response = self._make_request('GET', f'products.json?limit={limit}')
            
            if response and 'products' in response:
                return response['products']
            
            return []
            
        except Exception as e:
            self.logger.error(f"Error getting products: {e}")
            return []
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product from Shopify"""
        try:
            response = self._make_request('DELETE', f'products/{product_id}.json')
            
            if response is not None:
                self.logger.info(f"✅ Deleted product ID: {product_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error deleting product {product_id}: {e}")
            return False
