"""
Complete Shopify configuration widget with German-only content
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import requests
import time
from datetime import datetime

class ShopifyClient:
    def __init__(self, shop_url, access_token):
        self.shop_url = shop_url
        self.access_token = access_token
        if not shop_url.startswith('http'):
            if not shop_url.endswith('.myshopify.com'):
                shop_url = f"{shop_url}.myshopify.com"
            shop_url = f"https://{shop_url}"
        self.base_url = f"{shop_url}/admin/api/2024-01"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json'
        }
    
    def _validate_image_url(self, url):
        """Simple image URL validation"""
        try:
            if not url or not isinstance(url, str):
                return None
            url = url.strip()
            if not url.startswith(('http://', 'https://')):
                return None
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
            if any(ext in url.lower() for ext in valid_extensions) or 'wilo.com' in url.lower():
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        return url
                except:
                    pass
            return None
        except:
            return None
    
    def create_product(self, product_data):
        """Create product with German text only"""
        try:
            print("=" * 80)
            print("SHOPIFY PRODUCT CREATION - GERMAN ONLY")
            
            name = product_data.get('name', 'Wilo Product')
            short_description = product_data.get('short_description', '')
            advantages = product_data.get('advantages', [])
            category = product_data.get('category', 'Industrie Heizung')
            subcategory = product_data.get('subcategory', 'Heizungspumpen')
            
            print(f"Product: {name}")
            print(f"Description: {len(short_description)} chars")
            print(f"Advantages: {len(advantages)} items")
            
            # Build German description
            html_parts = []
            html_parts.append(f"<h1>{name}</h1>")
            
            if short_description and len(short_description.strip()) > 20:
                html_parts.append(f"<p>{short_description}</p>")
                print("ADDED REAL GERMAN DESCRIPTION")
            else:
                html_parts.append(f"<p>Professionelle {name} von Wilo für industrielle Anwendungen.</p>")
            
            html_parts.append(f"<p><strong>Anwendung:</strong> {category}</p>")
            html_parts.append(f"<p><strong>Produkttyp:</strong> {subcategory}</p>")
            
            if advantages and len(advantages) > 0:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    if advantage and len(advantage.strip()) > 10:
                        html_parts.append(f"<li>{advantage.strip()}</li>")
                html_parts.append("</ul>")
                print(f"ADDED {len(advantages)} GERMAN ADVANTAGES")
            else:
                html_parts.append("<h3>Hauptmerkmale</h3>")
                html_parts.append("<ul>")
                html_parts.append("<li>Hochwertige deutsche Ingenieurskunst</li>")
                html_parts.append("<li>Energieeffizienter Betrieb</li>")
                html_parts.append("<li>Zuverlässige Leistung für industrielle Anwendungen</li>")
                html_parts.append("</ul>")
            
            html_parts.append("<h3>Über Wilo</h3>")
            html_parts.append("<p>Wilo ist ein führender Hersteller von Pumpen und Pumpensystemen für Heizung, Kühlung, Klimatechnik, Wasserversorgung und Abwasserbehandlung.</p>")
            
            body_html = "\n".join(html_parts)
            
            # Process images with validation
            valid_images = []
            card_image = product_data.get('card_image_url', '')
            product_images = product_data.get('product_images', [])
            
            print(f"Processing images: card={bool(card_image)}, product={len(product_images)}")
            
            if card_image:
                validated = self._validate_image_url(card_image)
                if validated:
                    valid_images.append({
                        'src': validated, 
                        'alt': f"{name} - Produktbild"
                    })
                    print("Added validated card image")
            
            for i, img_url in enumerate(product_images[:15]):
                if img_url:
                    validated = self._validate_image_url(img_url)
                    if validated and validated not in [img['src'] for img in valid_images]:
                        valid_images.append({
                            'src': validated, 
                            'alt': f"{name} - Bild {i+1}"
                        })
                        print(f"Added validated image {i+1}")
            
            shopify_product = {
                'title': name,
                'body_html': body_html,
                'vendor': 'Wilo',
                'product_type': subcategory,
                'tags': f"Wilo, {category}, {subcategory}, Deutsche Qualität",
                'status': 'draft',
                'variants': [{
                    'title': 'Standard',
                    'price': '0.00',
                    'inventory_management': 'shopify',
                    'inventory_quantity': 0,
                    'requires_shipping': True,
                    'taxable': True,
                    'sku': f"WILO-{name.replace(' ', '-').replace('.', '').upper()[:20]}"
                }]
            }
            
            if valid_images:
                shopify_product['images'] = valid_images
                print(f"Total images added: {len(valid_images)}")
            
            print("Creating product in Shopify...")
            response = requests.post(
                f"{self.base_url}/products.json",
                headers=self.headers,
                json={'product': shopify_product},
                timeout=30
            )
            
            if response.status_code == 201:
                product = response.json()['product']
                print(f"SUCCESS: Created product {product['id']}")
                print("=" * 80)
                return product
            else:
                print(f"ERROR: {response.status_code} - {response.text}")
                print("=" * 80)
                return None
                
        except Exception as e:
            print(f"ERROR creating product: {e}")
            import traceback
            traceback.print_exc()
            return None

class ShopifyConfig(ttk.LabelFrame):
    def __init__(self, parent, settings):
        super().__init__(parent, text="Shopify Integration", padding="10")
        self.settings = settings
        self.is_connected = False
        self._create_widgets()
    
    def _create_widgets(self):
        # Connection Section
        connection_frame = ttk.LabelFrame(self, text="Verbindungseinstellungen", padding="5")
        connection_frame.pack(fill='x', pady=5)
        
        ttk.Label(connection_frame, text="Shop URL:").grid(row=0, column=0, sticky='w', pady=2)
        self.shop_url_var = tk.StringVar(value=getattr(self.settings, 'shopify_shop_url', ''))
        shop_entry = ttk.Entry(connection_frame, textvariable=self.shop_url_var, width=40)
        shop_entry.grid(row=0, column=1, sticky='w', padx=5)
        ttk.Label(connection_frame, text="(z.B., meinshop.myshopify.com)", font=('Arial', 8)).grid(row=0, column=2, sticky='w', padx=5)
        
        ttk.Label(connection_frame, text="Access Token:").grid(row=1, column=0, sticky='w', pady=2)
        self.access_token_var = tk.StringVar(value=getattr(self.settings, 'shopify_access_token', ''))
        token_entry = ttk.Entry(connection_frame, textvariable=self.access_token_var, width=40, show="*")
        token_entry.grid(row=1, column=1, sticky='w', padx=5)
        
        self.show_token_var = tk.BooleanVar()
        show_cb = ttk.Checkbutton(
            connection_frame, 
            text="Anzeigen", 
            variable=self.show_token_var,
            command=lambda: token_entry.config(show="" if self.show_token_var.get() else "*")
        )
        show_cb.grid(row=1, column=2, sticky='w', padx=5)
        
        button_frame = ttk.Frame(connection_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky='w')
        
        self.test_button = ttk.Button(button_frame, text="Verbindung testen", command=self.test_connection)
        self.test_button.pack(side='left', padx=5)
        
        self.save_button = ttk.Button(button_frame, text="Einstellungen speichern", command=self.save_settings)
        self.save_button.pack(side='left', padx=5)
        
        self.status_var = tk.StringVar(value="Nicht verbunden")
        status_label = ttk.Label(connection_frame, textvariable=self.status_var)
        status_label.grid(row=3, column=0, columnspan=3, pady=5, sticky='w')
        
        # Upload Section
        upload_frame = ttk.LabelFrame(self, text="Produkt Upload", padding="5")
        upload_frame.pack(fill='x', pady=5)
        
        upload_controls = ttk.Frame(upload_frame)
        upload_controls.pack(fill='x', pady=5)
        
        self.upload_button = ttk.Button(
            upload_controls,
            text="Gescrapte Produkte hochladen",
            command=self.upload_scraped_products,
            state='disabled'
        )
        self.upload_button.pack(side='left', padx=5)
        
        self.export_button = ttk.Button(upload_controls, text="Exportieren", command=self.export_products)
        self.export_button.pack(side='left', padx=5)
        
        self.progress_var = tk.StringVar(value="Bereit für Upload")
        ttk.Label(upload_frame, textvariable=self.progress_var).pack(pady=5)
        
        self.progress_bar = ttk.Progressbar(upload_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Upload options
        options_frame = ttk.LabelFrame(upload_frame, text="Upload Optionen", padding="5")
        options_frame.pack(fill='x', pady=5)
        
        self.draft_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Produkte als Entwürfe erstellen (empfohlen)",
            variable=self.draft_mode_var
        ).pack(anchor='w')
        
        # Results section
        results_frame = ttk.LabelFrame(self, text="Upload Ergebnisse", padding="5")
        results_frame.pack(fill='both', expand=True, pady=5)
        
        self.results_text = tk.Text(results_frame, height=8, state='disabled')
        scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        self.results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def test_connection(self):
        shop_url = self.shop_url_var.get().strip()
        access_token = self.access_token_var.get().strip()
        
        if not shop_url or not access_token:
            messagebox.showwarning("Fehlende Angaben", "Bitte Shop URL und Access Token eingeben")
            return
        
        self.status_var.set("Teste Verbindung...")
        self.test_button.config(state='disabled')
        
        thread = threading.Thread(target=self._test_connection_worker)
        thread.daemon = True
        thread.start()
    
    def _test_connection_worker(self):
        try:
            shop_url = self.shop_url_var.get().strip()
            access_token = self.access_token_var.get().strip()
            
            if not shop_url.startswith('http'):
                if not shop_url.endswith('.myshopify.com'):
                    shop_url = f"{shop_url}.myshopify.com"
                shop_url = f"https://{shop_url}"
            
            headers = {'X-Shopify-Access-Token': access_token, 'Content-Type': 'application/json'}
            response = requests.get(f"{shop_url}/admin/api/2024-01/shop.json", headers=headers, timeout=10)
            
            if response.status_code == 200:
                shop_data = response.json().get('shop', {})
                shop_name = shop_data.get('name', 'Unbekannt')
                self.after(0, self._update_connection_status, True, shop_name)
            else:
                self.after(0, self._update_connection_status, False, f"HTTP {response.status_code}")
        except Exception as e:
            self.after(0, self._update_connection_status, False, str(e))
    
    def _update_connection_status(self, success, info=None):
        try:
            if success:
                self.is_connected = True
                self.status_var.set(f"Verbunden mit {info}")
                self.upload_button.config(state='normal')
                messagebox.showinfo("Erfolg", f"Erfolgreich verbunden mit {info}!")
            else:
                self.is_connected = False
                self.status_var.set(f"Verbindung fehlgeschlagen: {info}")
                messagebox.showerror("Fehler", f"Verbindung fehlgeschlagen: {info}")
        finally:
            self.test_button.config(state='normal')
    
    def save_settings(self):
        try:
            if hasattr(self.settings, 'shopify_shop_url'):
                self.settings.shopify_shop_url = self.shop_url_var.get().strip()
            if hasattr(self.settings, 'shopify_access_token'):
                self.settings.shopify_access_token = self.access_token_var.get().strip()
            if hasattr(self.settings, 'save'):
                self.settings.save()
            messagebox.showinfo("Erfolg", "Einstellungen gespeichert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Speichern fehlgeschlagen: {e}")
    
    def upload_scraped_products(self):
        if not self.is_connected:
            messagebox.showwarning("Nicht verbunden", "Bitte zuerst Verbindung testen")
            return
        
        products = self.get_scraped_products()
        if not products:
            messagebox.showwarning("Keine Produkte", "Keine Produkte zum Hochladen gefunden")
            return
        
        result = messagebox.askyesno("Bestätigen", f"{len(products)} Produkte hochladen?")
        if not result:
            return
        
        self.upload_button.config(state='disabled')
        thread = threading.Thread(target=self._upload_worker, args=(products,))
        thread.daemon = True
        thread.start()
    
    def _upload_worker(self, products):
        try:
            client = ShopifyClient(self.shop_url_var.get(), self.access_token_var.get())
            successful = []
            failed = []
            
            self.after(0, lambda: self.progress_bar.config(maximum=len(products), value=0))
            
            for i, product in enumerate(products):
                self.after(0, lambda i=i, p=product: self.progress_var.set(f"Lade hoch {i+1}/{len(products)}: {p.get('name', 'Unbekannt')}"))
                
                result = client.create_product(product)
                if result:
                    successful.append({'product': product, 'shopify_id': result['id']})
                    print(f"SUCCESS: {product.get('name')} (ID: {result['id']})")
                else:
                    failed.append({'product': product, 'error': 'Erstellung fehlgeschlagen'})
                    print(f"FAILED: {product.get('name')}")
                
                self.after(0, lambda i=i: self.progress_bar.config(value=i+1))
                time.sleep(0.5)
            
            self.after(0, lambda: self._display_results(successful, failed))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Fehler", f"Upload fehlgeschlagen: {e}"))
        finally:
            self.after(0, lambda: self.upload_button.config(state='normal'))
            self.after(0, lambda: self.progress_var.set("Upload abgeschlossen"))
    
    def _display_results(self, successful, failed):
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.results_text.insert(tk.END, f"=== UPLOAD ERGEBNISSE - {timestamp} ===\n\n")
        
        self.results_text.insert(tk.END, f"Gesamt: {len(successful) + len(failed)}\n")
        self.results_text.insert(tk.END, f"Erfolgreich: {len(successful)}\n")
        self.results_text.insert(tk.END, f"Fehlgeschlagen: {len(failed)}\n\n")
        
        if successful:
            self.results_text.insert(tk.END, "=== ERFOLGREICH ===\n")
            for item in successful:
                product = item['product']
                shopify_id = item['shopify_id']
                self.results_text.insert(tk.END, f"✅ {product.get('name', 'Unbekannt')} (ID: {shopify_id})\n")
            self.results_text.insert(tk.END, "\n")
        
        if failed:
            self.results_text.insert(tk.END, "=== FEHLGESCHLAGEN ===\n")
            for item in failed:
                product = item['product']
                error = item.get('error', 'Unbekannter Fehler')
                self.results_text.insert(tk.END, f"❌ {product.get('name', 'Unbekannt')} - {error}\n")
        
        self.results_text.config(state='disabled')
        
        if len(failed) == 0:
            messagebox.showinfo("Abgeschlossen", f"Alle {len(successful)} Produkte erfolgreich hochgeladen!")
        else:
            messagebox.showwarning("Abgeschlossen mit Fehlern", f"Erfolgreich: {len(successful)}, Fehlgeschlagen: {len(failed)}")
    
    def export_products(self):
        products = self.get_scraped_products()
        if not products:
            messagebox.showwarning("Keine Produkte", "Keine Produkte zum Exportieren")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Produkte speichern",
            defaultextension=".json",
            filetypes=[("JSON Dateien", "*.json"), ("Alle Dateien", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exportiert", f"{len(products)} Produkte exportiert!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen: {e}")
    
    def get_scraped_products(self):
        return []
    
    def set_scraped_products_getter(self, getter_func):
        self.get_scraped_products = getter_func
    
    def get_settings(self):
        return {
            'shop_url': self.shop_url_var.get(),
            'access_token': self.access_token_var.get()
        }