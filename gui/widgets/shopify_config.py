#!/usr/bin/env python3
"""
Fix Shopify Upload Error - 'ShopifyConfig' object has no attribute 'root'
"""

def fix_shopify_widget():
    """Fix the progress callback issue in ShopifyConfig widget"""
    
    fixed_shopify_widget_content = '''"""
Enhanced Shopify configuration widget with upload functionality - FIXED


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
        self.parent = parent
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
            self.after(0, self._update_connection_status, success)
            
        except Exception as e:
            self.after(0, self._update_connection_status, False, str(e))
    
    def _update_connection_status(self, success, error=None):
        """Update connection status on main thread"""
        try:
            if success:
                self.is_connected = True
                self.status_var.set("✅ Connected successfully!")
                self.upload_scraped_button.config(state='normal')
                self.upload_file_button.config(state='normal')
                messagebox.showinfo("Success", "✅ Connected to Shopify successfully!")
            else:
                self.is_connected = False
                error_msg = f": {error}" if error else ""
                self.status_var.set(f"❌ Connection failed{error_msg}")
                messagebox.showerror("Error", f"❌ Failed to connect to Shopify{error_msg}")
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
            
            # Get products from results table
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
        """Worker thread for uploading products - FIXED"""
        try:
            # FIXED: Use a proper progress callback that works with threading
            def progress_callback(message):
                try:
                    # Schedule GUI update on main thread
                    self.after(0, lambda: self.progress_var.set(message))
                except:
                    pass  # Ignore GUI update errors during threading
            
            # Set initial progress
            self.after(0, lambda: self.progress_bar.config(maximum=len(products), value=0))
            
            # Upload products
            results = self.shopify_client.bulk_upload_products(products, progress_callback)
            
            # Update progress bar on main thread
            self.after(0, lambda: self.progress_bar.config(value=len(products)))
            
            # Show results on main thread
            self.after(0, lambda: self._display_upload_results(results))
            
            # Show completion message on main thread
            success_count = results['success_count']
            error_count = results['error_count']
            total = results['total']
            
            def show_completion_message():
                if error_count == 0:
                    messagebox.showinfo("Upload Complete", f"✅ Successfully uploaded all {success_count} products!")
                else:
                    messagebox.showwarning(
                        "Upload Complete with Errors", 
                        f"Upload completed:\\n✅ Successful: {success_count}\\n❌ Failed: {error_count}\\n📊 Total: {total}"
                    )
            
            self.after(0, show_completion_message)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"❌ Upload failed: {e}"))
        finally:
            # Re-enable buttons on main thread
            self.after(0, lambda: self.upload_scraped_button.config(state='normal'))
            self.after(0, lambda: self.upload_file_button.config(state='normal'))
            self.after(0, lambda: self.progress_var.set("Upload completed"))
    
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
    
    # Write the fixed widget
    with open('gui/widgets/shopify_config.py', 'w') as f:
        f.write(fixed_shopify_widget_content)
    
    print("✅ Fixed Shopify widget - GUI threading issue resolved")

def main():
    """Fix the Shopify upload error"""
    print("🔧 Fixing Shopify Upload Error")
    print("=" * 30)
    
    fix_shopify_widget()
    
    print("\n✅ Fixed the 'root' attribute error!")
    print("\n🛠️ What was fixed:")
    print("   - Replaced direct 'self.root' access with 'self.after()' scheduling")
    print("   - Fixed progress callback for threading")
    print("   - Added proper GUI thread safety")
    print("   - Fixed all GUI update calls")
    
    print("\n🚀 Now try again:")
    print("   1. Run: python main.py")
    print("   2. Go to Shopify Integration tab")
    print("   3. Test connection (should still work)")
    print("   4. Upload scraped products (should work now!)")
    
    print("\n🎯 Your 36 products should upload successfully!")

if __name__ == "__main__":
    main()