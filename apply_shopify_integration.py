#!/usr/bin/env python3
"""
Complete Shopify Integration for Wilo Scraper
"""

# 1. Enhanced Shopify Client
shopify_client_content = '''"""
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
            
            return "\\n".join(html_parts)
            
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
'''

# 2. Enhanced GUI Integration
enhanced_shopify_widget_content = '''"""
Enhanced Shopify configuration widget with upload functionality
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from datetime import datetime
from shopify.shopify_client import ShopifyClient

class ShopifyConfig(ttk.LabelFrame):
    """Enhanced Shopify configuration widget with upload functionality"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Shopify Integration", padding="10")
        self.settings = settings
        self.shopify_client = None
        self.is_connected = False
        self._create_widgets()
    
    def _create_widgets(self):
        """Create Shopify configuration widgets"""
        
        # Connection Section
        connection_frame = ttk.LabelFrame(self, text="Connection Settings", padding="5")
        connection_frame.pack(fill='x', pady=5)
        
        # Shop URL
        ttk.Label(connection_frame, text="Shop URL:").grid(row=0, column=0, sticky='w', pady=2)
        self.shop_url_var = tk.StringVar(value=self.settings.shopify_shop_url)
        shop_url_entry = ttk.Entry(connection_frame, textvariable=self.shop_url_var, width=40)
        shop_url_entry.grid(row=0, column=1, sticky='w', padx=5)
        ttk.Label(connection_frame, text="(e.g., mystore.myshopify.com)", font=('Arial', 8)).grid(row=0, column=2, sticky='w', padx=5)
        
        # Access Token
        ttk.Label(connection_frame, text="Access Token:").grid(row=1, column=0, sticky='w', pady=2)
        self.access_token_var = tk.StringVar(value=self.settings.shopify_access_token)
        token_entry = ttk.Entry(connection_frame, textvariable=self.access_token_var, width=40, show="*")
        token_entry.grid(row=1, column=1, sticky='w', padx=5)
        
        # Show/Hide token button
        self.show_token_var = tk.BooleanVar()
        show_token_cb = ttk.Checkbutton(
            connection_frame, 
            text="Show", 
            variable=self.show_token_var,
            command=lambda: token_entry.config(show="" if self.show_token_var.get() else "*")
        )
        show_token_cb.grid(row=1, column=2, sticky='w', padx=5)
        
        # Connection buttons
        button_frame = ttk.Frame(connection_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky='w')
        
        self.test_button = ttk.Button(
            button_frame,
            text="🔌 Test Connection",
            command=self.test_connection
        )
        self.test_button.pack(side='left', padx=5)
        
        self.save_button = ttk.Button(
            button_frame,
            text="💾 Save Settings",
            command=self.save_settings
        )
        self.save_button.pack(side='left', padx=5)
        
        # Connection Status
        self.status_var = tk.StringVar(value="Not connected")
        self.status_label = ttk.Label(connection_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=3, pady=5, sticky='w')
        
        # Upload Section
        upload_frame = ttk.LabelFrame(self, text="Product Upload", padding="5")
        upload_frame.pack(fill='x', pady=5)
        
        # Upload controls
        upload_controls = ttk.Frame(upload_frame)
        upload_controls.pack(fill='x', pady=5)
        
        self.upload_scraped_button = ttk.Button(
            upload_controls,
            text="🛒 Upload Scraped Products",
            command=self.upload_scraped_products,
            state='disabled'
        )
        self.upload_scraped_button.pack(side='left', padx=5)
        
        self.upload_file_button = ttk.Button(
            upload_controls,
            text="📁 Upload from JSON File",
            command=self.upload_from_file,
            state='disabled'
        )
        self.upload_file_button.pack(side='left', padx=5)
        
        self.export_button = ttk.Button(
            upload_controls,
            text="💾 Export Products",
            command=self.export_products
        )
        self.export_button.pack(side='left', padx=5)
        
        # Upload progress
        self.progress_var = tk.StringVar(value="Ready for upload")
        ttk.Label(upload_frame, textvariable=self.progress_var).pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(upload_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Upload options
        options_frame = ttk.LabelFrame(upload_frame, text="Upload Options", padding="5")
        options_frame.pack(fill='x', pady=5)
        
        self.draft_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Create products as drafts (recommended)",
            variable=self.draft_mode_var
        ).pack(anchor='w')
        
        self.skip_existing_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Skip products that already exist",
            variable=self.skip_existing_var
        ).pack(anchor='w')
        
        # Results section
        results_frame = ttk.LabelFrame(self, text="Upload Results", padding="5")
        results_frame.pack(fill='both', expand=True, pady=5)
        
        # Results text
        self.results_text = tk.Text(results_frame, height=8, state='disabled')
        results_scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side='left', fill='both', expand=True)
        results_scrollbar.pack(side='right', fill='y')
    
    def test_connection(self):
        """Test Shopify API connection"""
        try:
            # Update settings
            self.settings.shopify_shop_url = self.shop_url_var.get().strip()
            self.settings.shopify_access_token = self.access_token_var.get().strip()
            
            if not self.settings.shopify_shop_url or not self.settings.shopify_access_token:
                messagebox.showwarning("Missing Information", "Please enter both shop URL and access token.")
                return
            
            self.status_var.set("Testing connection...")
            self.test_button.config(state='disabled')
            
            # Test in separate thread
            thread = threading.Thread(target=self._test_connection_worker)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.status_var.set("❌ Connection test failed")
            messagebox.showerror("Error", f"Connection test failed: {e}")
            self.test_button.config(state='normal')
    
    def _test_connection_worker(self):
        """Worker thread for testing connection"""
        try:
            # Create Shopify client
            self.shopify_client = ShopifyClient(self.settings)
            
            # Test connection
            success = self.shopify_client.test_connection()
            
            # Update UI on main thread
            if success:
                self.is_connected = True
                self.status_var.set("✅ Connected successfully!")
                self.upload_scraped_button.config(state='normal')
                self.upload_file_button.config(state='normal')
                messagebox.showinfo("Success", "✅ Connected to Shopify successfully!")
            else:
                self.is_connected = False
                self.status_var.set("❌ Connection failed")
                messagebox.showerror("Error", "❌ Failed to connect to Shopify. Please check your credentials.")
            
        except Exception as e:
            self.is_connected = False
            self.status_var.set("❌ Connection error")
            messagebox.showerror("Error", f"❌ Connection error: {e}")
        finally:
            self.test_button.config(state='normal')
    
    def save_settings(self):
        """Save Shopify settings"""
        try:
            self.settings.shopify_shop_url = self.shop_url_var.get().strip()
            self.settings.shopify_access_token = self.access_token_var.get().strip()
            self.settings.save()
            
            messagebox.showinfo("Success", "✅ Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to save settings: {e}")
    
    def upload_scraped_products(self):
        """Upload currently scraped products to Shopify"""
        try:
            if not self.is_connected:
                messagebox.showwarning("Not Connected", "Please test connection first.")
                return
            
            # Get products from results table (you'll need to pass this from main window)
            products = self.get_scraped_products()
            
            if not products:
                messagebox.showwarning("No Products", "No products to upload. Please scrape some products first.")
                return
            
            # Confirm upload
            result = messagebox.askyesno(
                "Confirm Upload", 
                f"Upload {len(products)} products to Shopify?\\n\\nProducts will be created as {'drafts' if self.draft_mode_var.get() else 'active products'}."
            )
            
            if not result:
                return
            
            # Start upload in separate thread
            self.upload_scraped_button.config(state='disabled')
            self.upload_file_button.config(state='disabled')
            
            thread = threading.Thread(target=self._upload_worker, args=(products,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Upload failed: {e}")
    
    def upload_from_file(self):
        """Upload products from JSON file"""
        try:
            if not self.is_connected:
                messagebox.showwarning("Not Connected", "Please test connection first.")
                return
            
            # Select JSON file
            file_path = filedialog.askopenfilename(
                title="Select JSON file with products",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Load products from file
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            if not products:
                messagebox.showwarning("No Products", "No products found in the selected file.")
                return
            
            # Confirm upload
            result = messagebox.askyesno(
                "Confirm Upload", 
                f"Upload {len(products)} products from file to Shopify?"
            )
            
            if not result:
                return
            
            # Start upload
            self.upload_scraped_button.config(state='disabled')
            self.upload_file_button.config(state='disabled')
            
            thread = threading.Thread(target=self._upload_worker, args=(products,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ File upload failed: {e}")
    
    def _upload_worker(self, products):
        """Worker thread for uploading products"""
        try:
            def progress_callback(message):
                self.progress_var.set(message)
                self.root.update_idletasks()
            
            # Set initial progress
            self.progress_bar.config(maximum=len(products), value=0)
            
            # Upload products
            results = self.shopify_client.bulk_upload_products(products, progress_callback)
            
            # Update progress bar
            self.progress_bar.config(value=len(products))
            
            # Show results
            self._display_upload_results(results)
            
            # Show completion message
            success_count = results['success_count']
            error_count = results['error_count']
            total = results['total']
            
            if error_count == 0:
                messagebox.showinfo("Upload Complete", f"✅ Successfully uploaded all {success_count} products!")
            else:
                messagebox.showwarning(
                    "Upload Complete with Errors", 
                    f"Upload completed:\\n✅ Successful: {success_count}\\n❌ Failed: {error_count}\\n📊 Total: {total}"
                )
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Upload failed: {e}")
        finally:
            self.upload_scraped_button.config(state='normal')
            self.upload_file_button.config(state='normal')
            self.progress_var.set("Upload completed")
    
    def _display_upload_results(self, results):
        """Display upload results in the text widget"""
        try:
            self.results_text.config(state='normal')
            self.results_text.delete(1.0, tk.END)
            
            # Header
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.results_text.insert(tk.END, f"=== Upload Results - {timestamp} ===\\n\\n")
            
            # Summary
            self.results_text.insert(tk.END, f"Total Products: {results['total']}\\n")
            self.results_text.insert(tk.END, f"✅ Successful: {results['success_count']}\\n")
            self.results_text.insert(tk.END, f"❌ Failed: {results['error_count']}\\n\\n")
            
            # Successful uploads
            if results['successful']:
                self.results_text.insert(tk.END, "=== SUCCESSFUL UPLOADS ===\\n")
                for item in results['successful']:
                    product = item['product']
                    action = item.get('action', 'created')
                    shopify_id = item.get('shopify_id', 'Unknown')
                    
                    self.results_text.insert(tk.END, f"✅ {product.get('name', 'Unknown')} ")
                    self.results_text.insert(tk.END, f"({action}) - ID: {shopify_id}\\n")
                
                self.results_text.insert(tk.END, "\\n")
            
            # Failed uploads
            if results['failed']:
                self.results_text.insert(tk.END, "=== FAILED UPLOADS ===\\n")
                for item in results['failed']:
                    product = item['product']
                    error = item.get('error', 'Unknown error')
                    
                    self.results_text.insert(tk.END, f"❌ {product.get('name', 'Unknown')} ")
                    self.results_text.insert(tk.END, f"- Error: {error}\\n")
            
            self.results_text.config(state='disabled')
            self.results_text.see(tk.END)
            
        except Exception as e:
            print(f"Error displaying results: {e}")
    
    def export_products(self):
        """Export scraped products to JSON file"""
        try:
            products = self.get_scraped_products()
            
            if not products:
                messagebox.showwarning("No Products", "No products to export.")
                return
            
            # Select save location
            file_path = filedialog.asksaveasfilename(
                title="Save products as JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Save products
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Export Complete", f"✅ Exported {len(products)} products to:\\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Export failed: {e}")
    
    def get_scraped_products(self):
        """Get scraped products from the main application"""
        # This method should be overridden or connected to the main window
        # For now, return empty list
        return []
    
    def set_scraped_products_getter(self, getter_func):
        """Set function to get scraped products"""
        self.get_scraped_products = getter_func
    
    def get_settings(self):
        """Get current Shopify settings"""
        return {
            'shop_url': self.shop_url_var.get(),
            'access_token': self.access_token_var.get()
        }
'''

# 3. Enhanced Main Window Integration
enhanced_main_window_content = '''"""
Enhanced Main Window with Shopify Integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from gui.widgets.country_selector import CountrySelector
from gui.widgets.browser_settings import BrowserSettings
from gui.widgets.progress_tracker import ProgressTracker
from gui.widgets.results_table import ResultsTable
from gui.widgets.shopify_config import ShopifyConfig
from scraper.wilo_scraper import WiloScraper
from utils.logger import get_logger, LogCapture, GUILogHandler

class MainWindow:
    """Enhanced main application window with Shopify integration"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Initialize variables
        self.scraper = None
        self.is_scraping = False
        self.scraped_products = []  # Store all scraped products
        
        # Setup logging for GUI
        self.log_capture = LogCapture()
        self.gui_log_handler = GUILogHandler(self.log_capture)
        self.logger.addHandler(self.gui_log_handler)
        
        # Setup window
        self._setup_window()
        
        # Create GUI components
        self._create_widgets()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Wilo Product Scraper & Shopify Uploader")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create main widgets"""
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tab frames
        self.main_frame = ttk.Frame(self.notebook)
        self.shopify_frame = ttk.Frame(self.notebook)
        self.results_frame = ttk.Frame(self.notebook)
        
        # Add tabs
        self.notebook.add(self.main_frame, text="🚀 Main Scraper")
        self.notebook.add(self.shopify_frame, text="🛒 Shopify Integration")
        self.notebook.add(self.results_frame, text="📊 Results & Export")
        
        # Create main tab content
        self._create_main_tab()
        
        # Create Shopify tab content
        self._create_shopify_tab()
        
        # Create results tab content
        self._create_results_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_main_tab(self):
        """Create main scraping tab"""
        
        # Left panel for controls
        left_panel = ttk.Frame(self.main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Country selector
        self.country_selector = CountrySelector(left_panel, self.settings)
        self.country_selector.pack(fill=tk.X, pady=5)
        
        # Browser settings
        self.browser_settings = BrowserSettings(left_panel, self.settings)
        self.browser_settings.pack(fill=tk.X, pady=5)
        
        # Control buttons
        control_frame = ttk.LabelFrame(left_panel, text="Scraping Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(
            control_frame,
            text="🚀 Start Scraping",
            command=self.start_scraping
        )
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ Stop Scraping",
            command=self.stop_scraping,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=2)
        
        self.test_button = ttk.Button(
            control_frame,
            text="🧪 Test Navigation",
            command=self.test_navigation
        )
        self.test_button.pack(fill=tk.X, pady=2)
        
        # Quick Shopify upload
        shopify_quick_frame = ttk.LabelFrame(left_panel, text="Quick Shopify Upload", padding=10)
        shopify_quick_frame.pack(fill=tk.X, pady=5)
        
        self.quick_upload_button = ttk.Button(
            shopify_quick_frame,
            text="🛒 Upload to Shopify",
            command=self.quick_shopify_upload,
            state=tk.DISABLED
        )
        self.quick_upload_button.pack(fill=tk.X, pady=2)
        
        # Product count display
        count_frame = ttk.LabelFrame(left_panel, text="Product Count", padding=10)
        count_frame.pack(fill=tk.X, pady=5)
        
        self.product_count_var = tk.StringVar(value="0 products scraped")
        ttk.Label(count_frame, textvariable=self.product_count_var, font=('Arial', 12, 'bold')).pack()
        
        # Right panel for progress
        right_panel = ttk.Frame(self.main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress tracker
        self.progress_tracker = ProgressTracker(right_panel, self.log_capture)
        self.progress_tracker.pack(fill=tk.BOTH, expand=True)
    
    def _create_shopify_tab(self):
        """Create Shopify integration tab"""
        
        # Enhanced Shopify configuration
        self.shopify_config = ShopifyConfig(self.shopify_frame, self.settings)
        self.shopify_config.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Connect scraped products getter
        self.shopify_config.set_scraped_products_getter(lambda: self.scraped_products)
    
    def _create_results_tab(self):
        """Create results tab"""
        
        # Results table
        self.results_table = ResultsTable(self.results_frame)
        self.results_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Export and action buttons
        export_frame = ttk.Frame(self.results_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            export_frame,
            text="📄 Export to CSV",
            command=self.export_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="📋 Export to JSON",
            command=self.export_json
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="🗑️ Clear Results",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.results_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=4, state='disabled')
        self.stats_text.pack(fill=tk.X)
    
    def _connect_signals(self):
        """Connect widget signals"""
        try:
            # Variable tracing for settings
            if hasattr(tk.StringVar, 'trace_add'):
                # Modern Tkinter
                pass  # Add traces if needed
            else:
                # Older Tkinter
                pass
        except Exception as e:
            self.logger.warning(f"Could not set up variable traces: {e}")
    
    def start_scraping(self):
        """Start the enhanced scraping process"""
        if self.is_scraping:
            return
        
        try:
            # Get selected country
            country_key = self.country_selector.get_selected_country_key()
            
            # Update browser settings
            browser_settings = self.browser_settings.get_settings()
            self.settings.headless_mode = browser_settings['headless_mode']
            self.settings.browser_timeout = browser_settings['browser_timeout']
            self.settings.page_load_delay = browser_settings['page_load_delay']
            
            # Create enhanced scraper
            self.scraper = WiloScraper(self.settings)
            
            # Set callbacks
            self.scraper.set_progress_callback(self.progress_tracker.update_progress)
            self.scraper.set_products_callback(self.add_product)
            
            # Update UI
            self.is_scraping = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Enhanced scraping in progress...")
            
            # Start scraping in separate thread
            self.scraping_thread = threading.Thread(
                target=self._scraping_worker,
                args=(country_key,)
            )
            self.scraping_thread.daemon = True
            self.scraping_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start scraping: {e}")
            messagebox.showerror("Error", f"Failed to start scraping: {e}")
            self._reset_scraping_ui()
    
    def _scraping_worker(self, country_key):
        """Enhanced worker function for scraping thread"""
        try:
            products = self.scraper.start_scraping(country_key)
            
            # Store products
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.root.after(0, self._on_scraping_completed, len(products))
            
        except Exception as e:
            self.logger.error(f"Scraping worker failed: {e}")
            self.root.after(0, self._on_scraping_failed, str(e))
    
    def _on_scraping_completed(self, product_count):
        """Handle enhanced scraping completion"""
        self.status_var.set(f"Enhanced scraping completed! Found {product_count} products")
        self._reset_scraping_ui()
        self._update_product_count()
        self._update_statistics()
        
        # Enable Shopify upload if products were found
        if product_count > 0:
            self.quick_upload_button.config(state=tk.NORMAL)
        
        messagebox.showinfo("Success", f"✅ Enhanced scraping completed!\\n\\nFound {product_count} products\\nTotal products: {len(self.scraped_products)}")
    
    def _on_scraping_failed(self, error_message):
        """Handle scraping failure"""
        self.status_var.set("Scraping failed")
        self._reset_scraping_ui()
        messagebox.showerror("Error", f"❌ Scraping failed: {error_message}")
    
    def add_product(self, product_data):
        """Add product to results (enhanced)"""
        # Add to results table
        self.results_table.add_product(product_data)
        
        # Update count
        self._update_product_count()
    
    def _update_product_count(self):
        """Update product count display"""
        count = len(self.scraped_products)
        self.product_count_var.set(f"{count} products scraped")
    
    def _update_statistics(self):
        """Update statistics display"""
        try:
            if not self.scraped_products:
                return
            
            # Calculate statistics
            total_products = len(self.scraped_products)
            categories = set(p.get('category', 'Unknown') for p in self.scraped_products)
            subcategories = set(p.get('subcategory', 'Unknown') for p in self.scraped_products)
            
            # Update stats text
            self.stats_text.config(state='normal')
            self.stats_text.delete(1.0, tk.END)
            
            stats = f"Total Products: {total_products}\\n"
            stats += f"Categories: {len(categories)}\\n"
            stats += f"Subcategories: {len(subcategories)}\\n"
            stats += f"Average per Category: {total_products / len(categories):.1f}"
            
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def quick_shopify_upload(self):
        """Quick Shopify upload from main tab"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Products", "No products to upload. Please scrape some products first.")
                return
            
            # Switch to Shopify tab
            self.notebook.select(1)
            
            # Show upload confirmation
            result = messagebox.askyesno(
                "Quick Upload", 
                f"Upload {len(self.scraped_products)} scraped products to Shopify?\\n\\nThis will use your current Shopify settings."
            )
            
            if result:
                # Trigger upload on Shopify tab
                self.shopify_config.upload_scraped_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Quick upload failed: {e}")
    
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.scraper:
            self.scraper.stop()
        
        self.status_var.set("Stopping scraping...")
        self._reset_scraping_ui()
    
    def _reset_scraping_ui(self):
        """Reset UI after scraping"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def test_navigation(self):
        """Test navigation to Wilo website"""
        try:
            self.status_var.set("Testing navigation...")
            
            # Create temporary scraper
            test_scraper = WiloScraper(self.settings)
            test_scraper.set_progress_callback(self.progress_tracker.update_progress)
            
            # Run test in separate thread
            test_thread = threading.Thread(target=self._test_navigation_worker, args=(test_scraper,))
            test_thread.daemon = True
            test_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start navigation test: {e}")
            messagebox.showerror("Error", f"Navigation test failed: {e}")
    
    def _test_navigation_worker(self, test_scraper):
        """Worker function for navigation test"""
        try:
            success = test_scraper.test_navigation()
            
            # Update UI on main thread
            self.root.after(0, self._on_navigation_test_completed, success)
            
        except Exception as e:
            self.logger.error(f"Navigation test worker failed: {e}")
            self.root.after(0, self._on_navigation_test_failed, str(e))
    
    def _on_navigation_test_completed(self, success):
        """Handle navigation test completion"""
        if success:
            self.status_var.set("Navigation test successful!")
            messagebox.showinfo("Success", "✅ Navigation test successful!")
        else:
            self.status_var.set("Navigation test failed")
            messagebox.showerror("Error", "❌ Navigation test failed")
    
    def _on_navigation_test_failed(self, error_message):
        """Handle navigation test failure"""
        self.status_var.set("Navigation test failed")
        messagebox.showerror("Error", f"❌ Navigation test failed: {error_message}")
    
    def export_csv(self):
        """Export results to CSV"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            from tkinter import filedialog
            import csv
            
            file_path = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'category', 'subcategory', 'price', 'description', 'country', 'status']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.scraped_products:
                    row = {field: product.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            messagebox.showinfo("Export Complete", f"✅ Exported {len(self.scraped_products)} products to CSV!")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ CSV export failed: {e}")
    
    def export_json(self):
        """Export results to JSON"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            from tkinter import filedialog
            import json
            
            file_path = filedialog.asksaveasfilename(
                title="Export to JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export to JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_products, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Export Complete", f"✅ Exported {len(self.scraped_products)} products to JSON!")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ JSON export failed: {e}")
    
    def clear_results(self):
        """Clear all results"""
        try:
            result = messagebox.askyesno("Clear Results", "Clear all scraped products?\\n\\nThis cannot be undone.")
            
            if result:
                self.scraped_products.clear()
                self.results_table.clear()
                self._update_product_count()
                self._update_statistics()
                self.quick_upload_button.config(state=tk.DISABLED)
                self.status_var.set("Results cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
'''

def main():
    """Apply Shopify integration to the project"""
    print("🛒 Adding Complete Shopify Integration to Wilo Scraper")
    print("=" * 60)
    
    # Create Shopify client file
    with open('shopify/shopify_client.py', 'w') as f:
        f.write(shopify_client_content)
    print("✅ Created enhanced shopify/shopify_client.py")
    
    # Update Shopify widget
    with open('gui/widgets/shopify_config.py', 'w') as f:
        f.write(enhanced_shopify_widget_content)
    print("✅ Enhanced gui/widgets/shopify_config.py")
    
    # Update main window
    with open('gui/main_window.py', 'w') as f:
        f.write(enhanced_main_window_content)
    print("✅ Enhanced gui/main_window.py")
    
    print("\n🎉 Shopify Integration Complete!")
    print("\n🚀 New Features Added:")
    print("   ✅ Full Shopify API integration")
    print("   ✅ Bulk product upload with progress tracking")
    print("   ✅ Smart duplicate detection")
    print("   ✅ Enhanced product descriptions with HTML")
    print("   ✅ Automatic SKU generation")
    print("   ✅ Metafields for additional data")
    print("   ✅ Upload from JSON files")
    print("   ✅ Detailed upload results")
    print("   ✅ Quick upload from main tab")
    print("   ✅ Enhanced GUI with 3 tabs")
    
    print("\n📋 Setup Instructions:")
    print("1. Get your Shopify credentials:")
    print("   - Go to your Shopify admin")
    print("   - Navigate to Apps → Develop apps")
    print("   - Create a private app")
    print("   - Add permissions: read_products, write_products")
    print("   - Copy the Admin API access token")
    
    print("\n2. Run the application:")
    print("   python main.py")
    
    print("\n3. Configure Shopify:")
    print("   - Go to 'Shopify Integration' tab")
    print("   - Enter your store URL (e.g., mystore.myshopify.com)")
    print("   - Enter your access token")
    print("   - Click 'Test Connection'")
    
    print("\n4. Use the integration:")
    print("   - Scrape products in 'Main Scraper' tab")
    print("   - Upload to Shopify using 'Upload to Shopify' button")
    print("   - Monitor progress and results")

if __name__ == "__main__":
    main()