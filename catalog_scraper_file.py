#!/usr/bin/env python3
"""
Create the new catalog scraper file in your project
"""

import os
from pathlib import Path

def create_catalog_scraper():
    """Create the catalog scraper file"""
    
    scraper_content = '''"""
Enhanced Wilo Catalog Scraper for new catalog page
Scrapes from: https://wilo.com/de/de/Katalog/de/anwendung/industrie/heizung/heizung
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraper.browser_manager import BrowserManager
from utils.logger import get_logger

class WiloCatalogScraper:
    """New catalog scraper for Wilo products from catalog page"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        
        # Callback for progress updates
        self.progress_callback = None
        self.products_callback = None
        
        # Base URL for the new catalog
        self.catalog_url = "https://wilo.com/de/de/Katalog/de/anwendung/industrie/heizung/heizung"
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_products_callback(self, callback):
        """Set callback for product updates"""
        self.products_callback = callback
        
    def start_scraping(self, max_products=2):
        """Start catalog scraping process"""
        try:
            self.is_running = True
            self.logger.info(f"Starting catalog scraping for max {max_products} products")
            
            if self.progress_callback:
                self.progress_callback("Initializing browser for catalog scraping...", start_progress=True)
            
            # Setup browser
            if not self.browser_manager.setup_driver():
                raise Exception("Failed to setup browser")
                
            driver = self.browser_manager.get_driver()
            
            if self.progress_callback:
                self.progress_callback("Navigating to Wilo catalog page...")
            
            # Navigate to catalog page
            self.logger.info("Navigating to Wilo catalog page...")
            driver.get(self.catalog_url)
            time.sleep(5)
            
            self.browser_manager.take_screenshot("catalog_step1_initial_page.png")
            
            if self.progress_callback:
                self.progress_callback("Finding product cards...")
                
            # Find and process product cards
            all_products = self._extract_products_from_cards(max_products)
            
            if self.progress_callback:
                self.progress_callback(f"Catalog scraping completed! Found {len(all_products)} products", stop_progress=True)
                
            self.logger.info(f"Catalog scraping completed. Found {len(all_products)} products")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Catalog scraping failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Catalog scraping failed: {e}", stop_progress=True)
            return []
        finally:
            self.browser_manager.quit()
    
    def _extract_products_from_cards(self, max_products):
        """Extract products from card elements"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            
            # Wait for cards to load
            time.sleep(5)
            
            # Find all product cards using the structure you provided
            card_selector = "//div[contains(@class, 'card cl-overview h-100 rebrush')]"
            
            try:
                cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, card_selector)))
                self.logger.info(f"Found {len(cards)} product cards")
            except TimeoutException:
                self.logger.error("No product cards found")
                return []
            
            # Limit cards to max_products
            cards_to_process = cards[:max_products]
            self.logger.info(f"Processing {len(cards_to_process)} cards (limited by max_products={max_products})")
            
            all_products = []
            
            for i, card in enumerate(cards_to_process):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Processing product card {i+1}/{len(cards_to_process)}")
                
                try:
                    # Extract basic info from card
                    card_data = self._extract_card_data(card, i)
                    
                    if card_data:
                        # Click on card to go to product detail page
                        product_detail = self._get_product_details(card, card_data, i)
                        
                        if product_detail:
                            all_products.append(product_detail)
                            
                            # Update products in real-time
                            if self.products_callback:
                                self.products_callback(product_detail)
                            
                            self.logger.info(f"Successfully extracted product: {product_detail['name']}")
                        else:
                            self.logger.warning(f"Failed to get details for card {i+1}")
                    
                    # Small delay between cards
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing card {i+1}: {e}")
                    continue
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from cards: {e}")
            return []
    
    def _extract_card_data(self, card, index):
        """Extract data from a single product card"""
        try:
            # Extract product name from card footer
            try:
                name_element = card.find_element(By.XPATH, ".//div[@class='card-footer']//h3")
                product_name = name_element.text.strip()
            except:
                self.logger.warning(f"Could not find product name in card {index+1}")
                return None
            
            # Extract image from card
            image_url = ""
            try:
                img_element = card.find_element(By.XPATH, ".//img")
                img_src = img_element.get_attribute('src')
                if img_src:
                    # Convert relative URL to absolute
                    if img_src.startswith('//'):
                        image_url = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        image_url = f"https://wilo.com{img_src}"
                    else:
                        image_url = img_src
            except:
                self.logger.warning(f"Could not find image in card {index+1}")
            
            # Extract product link
            product_link = ""
            try:
                link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                href = link_element.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        product_link = f"https://wilo.com{href}"
                    else:
                        product_link = href
            except:
                self.logger.warning(f"Could not find product link in card {index+1}")
            
            card_data = {
                'name': product_name,
                'card_image_url': image_url,
                'product_link': product_link,
                'card_index': index
            }
            
            self.logger.info(f"Extracted card data: {product_name}")
            return card_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract card data: {e}")
            return None
    
    def _get_product_details(self, card, card_data, index):
        """Click on card and extract detailed product information"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Store current window handle
            main_window = driver.current_window_handle
            
            # Click on the card link
            try:
                link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                
                # Use JavaScript click to avoid potential overlay issues
                driver.execute_script("arguments[0].click();", link_element)
                self.logger.info(f"Clicked on product card: {card_data['name']}")
                
                # Wait for page to load
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Failed to click on card: {e}")
                return None
            
            # Take screenshot of product page
            self.browser_manager.take_screenshot(f"catalog_step2_product_{index}_page.png")
            
            # Extract detailed product information
            product_details = self._extract_product_page_details(card_data)
            
            # Go back to main page for next product
            driver.back()
            time.sleep(3)
            
            return product_details
            
        except Exception as e:
            self.logger.error(f"Failed to get product details: {e}")
            return None
    
    def _extract_product_page_details(self, card_data):
        """Extract detailed information from product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Extract all product images and videos
            media_items = self._extract_media_items()
            
            # Extract product short description (left side content)
            short_description = self._extract_short_description()
            
            # Extract advantages/benefits (Ihre Vorteile)
            advantages = self._extract_advantages()
            
            # Extract long description
            long_description = self._extract_long_description()
            
            # Create comprehensive product object
            product = {
                'id': f"catalog_{card_data['card_index']+1}_{int(time.time())}",
                'name': card_data['name'],
                'category': 'Industrie Heizung',
                'subcategory': 'Heizungspumpen',
                'source': 'catalog',
                
                # Images and media
                'card_image_url': card_data['card_image_url'],
                'product_images': media_items['images'],
                'product_videos': media_items['videos'],
                'all_media': media_items['all_media'],
                
                # Descriptions
                'short_description': short_description,
                'advantages': advantages,
                'long_description': long_description,
                'full_description': self._build_full_description(short_description, advantages, long_description),
                
                # Additional data
                'product_url': driver.current_url,
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'specifications': {
                    'brand': 'Wilo',
                    'series': card_data['name'],
                    'application': 'Industrie Heizung',
                    'type': 'Heizungspumpe'
                },
                'price': 'Price on request',
                'currency': 'EUR',
                'country': 'Germany',
                'status': 'Catalog Product - Real Extraction'
            }
            
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to extract product page details: {e}")
            return None
    
    def _extract_media_items(self):
        """Extract all images and videos from product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            media_items = {
                'images': [],
                'videos': [],
                'all_media': []
            }
            
            # Find all images on the product page
            try:
                # Look for carousel or gallery images
                img_selectors = [
                    "//div[contains(@class, 'carousel')]//img",
                    "//div[contains(@class, 'gallery')]//img", 
                    "//div[contains(@class, 'cl-gutters')]//img",
                    "//img[contains(@src, 'wilo')]"
                ]
                
                for selector in img_selectors:
                    try:
                        images = driver.find_elements(By.XPATH, selector)
                        for img in images:
                            src = img.get_attribute('src')
                            if src and src not in media_items['images']:
                                # Convert to absolute URL
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                media_items['images'].append(src)
                                media_items['all_media'].append({
                                    'type': 'image',
                                    'url': src,
                                    'alt': img.get_attribute('alt') or ''
                                })
                    except:
                        continue
                
            except Exception as e:
                self.logger.debug(f"Image extraction failed: {e}")
            
            # Find videos
            try:
                video_selectors = [
                    "//video//source",
                    "//iframe[contains(@src, 'video')]",
                    "//div[contains(@class, 'video')]//iframe"
                ]
                
                for selector in video_selectors:
                    try:
                        videos = driver.find_elements(By.XPATH, selector)
                        for video in videos:
                            src = video.get_attribute('src')
                            if src and src not in media_items['videos']:
                                media_items['videos'].append(src)
                                media_items['all_media'].append({
                                    'type': 'video',
                                    'url': src,
                                    'title': ''
                                })
                    except:
                        continue
                        
            except Exception as e:
                self.logger.debug(f"Video extraction failed: {e}")
            
            self.logger.info(f"Extracted {len(media_items['images'])} images and {len(media_items['videos'])} videos")
            return media_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract media items: {e}")
            return {'images': [], 'videos': [], 'all_media': []}
    
    def _extract_short_description(self):
        """Extract short description from left side of product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            short_desc_selectors = [
                "//div[contains(@class, 'product-info')]//p",
                "//div[contains(@class, 'description')]//p",
                "//h3[following-sibling::div/p]//following-sibling::div//p",
                "//div[@class='pl-md-8']//p"
            ]
            
            short_description = ""
            
            for selector in short_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        paragraphs = []
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 20:  # Only meaningful paragraphs
                                paragraphs.append(text)
                        
                        if paragraphs:
                            short_description = " ".join(paragraphs)
                            break
                            
                except:
                    continue
            
            self.logger.info(f"Extracted short description: {len(short_description)} characters")
            return short_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract short description: {e}")
            return ""
    
    def _extract_advantages(self):
        """Extract advantages/benefits (Ihre Vorteile) section"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for the advantages section with "Ihre Vorteile" header
            advantages_selectors = [
                "//div[contains(@class, 'cl-your-advantages')]//ul//li",
                "//h3[contains(text(), 'Ihre Vorteile')]//following-sibling::div//ul//li",
                "//h3[contains(text(), 'Vorteile')]//following-sibling::div//ul//li"
            ]
            
            advantages = []
            
            for selector in advantages_selectors:
                try:
                    li_elements = driver.find_elements(By.XPATH, selector)
                    if li_elements:
                        for li in li_elements:
                            text = li.text.strip()
                            if text:
                                advantages.append(text)
                        break
                except:
                    continue
            
            self.logger.info(f"Extracted {len(advantages)} advantages")
            return advantages
            
        except Exception as e:
            self.logger.error(f"Failed to extract advantages: {e}")
            return []
    
    def _extract_long_description(self):
        """Extract long description and other content sections"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for various content sections
            long_desc_selectors = [
                "//div[contains(@class, 'description')]",
                "//div[contains(@class, 'content')]//div[contains(@class, 'text')]",
                "//div[contains(@class, 'product-details')]",
                "//div[contains(@class, 'two-cols-section')]//div[contains(@class, 'text-module')]"
            ]
            
            long_description_parts = []
            
            for selector in long_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 50:  # Only substantial content
                            # Clean up the text
                            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                            if text not in long_description_parts:
                                long_description_parts.append(text)
                except:
                    continue
            
            long_description = "\\n\\n".join(long_description_parts)
            
            self.logger.info(f"Extracted long description: {len(long_description)} characters")
            return long_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract long description: {e}")
            return ""
    
    def _build_full_description(self, short_desc, advantages, long_desc):
        """Build comprehensive description for Shopify"""
        try:
            html_parts = []
            
            # Short description
            if short_desc:
                html_parts.append(f"<div class='product-intro'>{short_desc}</div>")
            
            # Advantages
            if advantages:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    html_parts.append(f"<li>{advantage}</li>")
                html_parts.append("</ul>")
            
            # Long description
            if long_desc:
                # Split long description into paragraphs
                paragraphs = long_desc.split('\\n\\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"<p>{paragraph.strip()}</p>")
            
            # Brand information
            html_parts.append("<h3>Über Wilo</h3>")
            html_parts.append("<p>Wilo ist ein führender Hersteller von Pumpen und Pumpensystemen für Heizung, Kühlung, Klimatechnik, Wasserversorgung und Abwasserbehandlung.</p>")
            
            return "\\n".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to build full description: {e}")
            return short_desc or "Wilo Produkt"
    
    def test_navigation(self):
        """Test navigation to catalog page"""
        try:
            self.logger.info("Testing catalog navigation...")
            
            if self.progress_callback:
                self.progress_callback("Testing catalog navigation...", start_progress=True)
            
            if not self.browser_manager.setup_driver():
                return False
                
            driver = self.browser_manager.get_driver()
            driver.get(self.catalog_url)
            
            time.sleep(5)
            self.browser_manager.take_screenshot("catalog_navigation_test.png")
            
            # Check if we're on the right page
            if "wilo.com" in driver.current_url and "katalog" in driver.current_url.lower():
                self.logger.info("Catalog navigation test completed successfully")
                if self.progress_callback:
                    self.progress_callback("Catalog navigation test successful!", stop_progress=True)
                return True
            else:
                self.logger.error("Catalog navigation test failed - unexpected page")
                if self.progress_callback:
                    self.progress_callback("Catalog navigation test failed", stop_progress=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Catalog navigation test failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Catalog navigation test failed: {e}", stop_progress=True)
            return False
        finally:
            self.browser_manager.quit()
    
    def stop(self):
        """Stop scraping"""
        self.logger.info("Stopping catalog scraper...")
        self.is_running = False
        if self.progress_callback:
            self.progress_callback("Catalog scraping stopped by user", stop_progress=True)
'''
    
    # Write the file
    with open('scraper/wilo_catalog_scraper.py', 'w') as f:
        f.write(scraper_content)
    
    print("✅ Created scraper/wilo_catalog_scraper.py")

def create_enhanced_main_window():
    """Update main window to use the enhanced controller"""
    
    main_window_content = '''"""
Enhanced Main Window with dual scraper support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from gui.widgets.progress_tracker import ProgressTracker
from gui.widgets.results_table import ResultsTable
from gui.widgets.shopify_config import ShopifyConfig
from gui.widgets.enhanced_scraper_controller import EnhancedScraperController
from utils.logger import get_logger, LogCapture, GUILogHandler

class MainWindow:
    """Enhanced main application window with dual scraper support"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Initialize variables
        self.scraped_products = []
        
        # Setup logging for GUI
        self.log_capture = LogCapture()
        self.gui_log_handler = GUILogHandler(self.log_capture)
        self.logger.addHandler(self.gui_log_handler)
        
        # Setup window
        self._setup_window()
        
        # Create GUI components
        self._create_widgets()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Wilo Product Scraper & Shopify Uploader - Enhanced Edition")
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
        self.notebook.add(self.main_frame, text="🚀 Enhanced Scraper")
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
        self.status_var.set("Ready - Choose between Catalog or Original scraper")
        
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_main_tab(self):
        """Create main scraping tab with enhanced controller"""
        
        # Left panel for enhanced controls
        left_panel = ttk.Frame(self.main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Enhanced scraper controller
        self.scraper_controller = EnhancedScraperController(left_panel, self.settings)
        self.scraper_controller.pack(fill=tk.X, pady=5)
        
        # Set callbacks
        self.scraper_controller.set_progress_callback(self.update_progress)
        self.scraper_controller.set_products_callback(self.add_product)
        
        # Quick actions
        quick_frame = ttk.LabelFrame(left_panel, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X, pady=5)
        
        self.upload_button = ttk.Button(
            quick_frame,
            text="🛒 Upload to Shopify",
            command=self.quick_shopify_upload,
            state=tk.DISABLED
        )
        self.upload_button.pack(fill=tk.X, pady=2)
        
        ttk.Button(
            quick_frame,
            text="📊 View Results",
            command=self.view_results
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            quick_frame,
            text="🗑️ Clear All",
            command=self.clear_all_results
        ).pack(fill=tk.X, pady=2)
        
        # Product statistics
        stats_frame = ttk.LabelFrame(left_panel, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, state='disabled')
        self.stats_text.pack(fill=tk.X)
        
        # Right panel for progress and logs
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
        
        # Results summary
        summary_frame = ttk.LabelFrame(self.results_frame, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=8, state='disabled')
        self.summary_text.pack(fill=tk.X)
    
    def update_progress(self, message, start_progress=False, stop_progress=False):
        """Update progress display"""
        self.status_var.set(message)
        self.progress_tracker.update_progress(message, start_progress, stop_progress)
    
    def add_product(self, product_data):
        """Add product to results"""
        self.scraped_products.append(product_data)
        self.results_table.add_product(product_data)
        self._update_statistics()
        
        # Enable upload button if we have products
        if len(self.scraped_products) > 0:
            self.upload_button.config(state=tk.NORMAL)
    
    def _update_statistics(self):
        """Update statistics display"""
        try:
            if not self.scraped_products:
                return
            
            # Calculate statistics
            total_products = len(self.scraped_products)
            catalog_products = sum(1 for p in self.scraped_products if p.get('source') == 'catalog')
            original_products = total_products - catalog_products
            
            categories = set(p.get('category', 'Unknown') for p in self.scraped_products)
            
            # Update stats text
            self.stats_text.config(state='normal')
            self.stats_text.delete(1.0, tk.END)
            
            stats = f"Total Products: {total_products}\n"
            stats += f"Catalog Products: {catalog_products}\n"
            stats += f"Original Products: {original_products}\n"
            stats += f"Unique Categories: {len(categories)}\n"
            
            if self.scraped_products:
                last_product = self.scraped_products[-1]
                stats += f"Last Added: {last_product.get('name', 'Unknown')[:30]}..."
            
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def quick_shopify_upload(self):
        """Quick Shopify upload"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Products", "No products to upload.")
                return
            
            # Switch to Shopify tab
            self.notebook.select(1)
            
            # Show upload confirmation
            result = messagebox.askyesno(
                "Quick Upload", 
                f"Upload {len(self.scraped_products)} products to Shopify?\n\n"
                f"Catalog products: {sum(1 for p in self.scraped_products if p.get('source') == 'catalog')}\n"
                f"Original products: {sum(1 for p in self.scraped_products if p.get('source') != 'catalog')}"
            )
            
            if result:
                self.shopify_config.upload_scraped_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Quick upload failed: {e}")
    
    def view_results(self):
        """View detailed results"""
        self.scraper_controller.show_results()
    
    def clear_all_results(self):
        """Clear all results"""
        try:
            if not self.scraped_products:
                messagebox.showinfo("No Data", "No products to clear.")
                return
            
            result = messagebox.askyesno(
                "Clear All Results", 
                f"Clear all {len(self.scraped_products)} scraped products?\n\nThis cannot be undone."
            )
            
            if result:
                self.scraped_products.clear()
                self.scraper_controller.clear_results()
                self.results_table.clear()
                self._update_statistics()
                self.upload_button.config(state=tk.DISABLED)
                self.status_var.set("All results cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
    
    def export_csv(self):
        """Export results to CSV"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            from tkinter import filedialog
            import csv
            from datetime import datetime
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"wilo_products_{timestamp}.csv"
            
            file_path = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                initialvalue=default_filename,
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'source', 'category', 'subcategory', 'short_description', 'price', 'country', 'status']
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
            from datetime import datetime
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"wilo_products_{timestamp}.json"
            
            file_path = filedialog.asksaveasfilename(
                title="Export to JSON",
                defaultextension=".json",
                initialvalue=default_filename,
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
        """Clear results table"""
        try:
            result = messagebox.askyesno("Clear Results", "Clear results table?\n\nThis will not affect scraped products.")
            
            if result:
                self.results_table.clear()
                self.status_var.set("Results table cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
'''
    
    with open('gui/main_window.py', 'w') as f:
        f.write(main_window_content)
    
    print("✅ Updated gui/main_window.py")

def create_enhanced_controller():
    """Create the enhanced scraper controller"""
    
    controller_content = '''"""
Enhanced scraper controller widget with dual scraper support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scraper.wilo_scraper import WiloScraper
from scraper.wilo_catalog_scraper import WiloCatalogScraper
from gui.widgets.country_selector import CountrySelector
from gui.widgets.browser_settings import BrowserSettings

class EnhancedScraperController(ttk.LabelFrame):
    """Enhanced controller for both original and catalog scrapers"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Enhanced Scraping Controls", padding="10")
        
        self.parent = parent
        self.settings = settings
        self.scraped_products = []
        
        # Scraper instances
        self.original_scraper = None
        self.catalog_scraper = None
        self.is_scraping = False
        
        # Callbacks
        self.progress_callback = None
        self.products_callback = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create enhanced control widgets"""
        
        # Scraper Selection
        scraper_frame = ttk.LabelFrame(self, text="Scraper Selection", padding="5")
        scraper_frame.pack(fill='x', pady=5)
        
        self.scraper_type_var = tk.StringVar(value="catalog")
        
        ttk.Radiobutton(
            scraper_frame,
            text="🆕 New Catalog Scraper (wilo.com/katalog)",
            variable=self.scraper_type_var,
            value="catalog"
        ).pack(anchor='w')
        
        ttk.Radiobutton(
            scraper_frame,
            text="📊 Original Select Scraper (select.wilo.com)",
            variable=self.scraper_type_var,
            value="original"
        ).pack(anchor='w')
        
        # Country Selection (for original scraper only)
        self.country_frame = ttk.LabelFrame(self, text="Country Selection (Original Scraper Only)", padding="5")
        self.country_frame.pack(fill='x', pady=5)
        
        self.country_selector = CountrySelector(self.country_frame, self.settings)
        self.country_selector.pack(fill='x')
        
        # Product Limit Control
        limit_frame = ttk.LabelFrame(self, text="Product Extraction Limits", padding="5")
        limit_frame.pack(fill='x', pady=5)
        
        # Catalog scraper limit
        catalog_limit_frame = ttk.Frame(limit_frame)
        catalog_limit_frame.pack(fill='x', pady=2)
        
        ttk.Label(catalog_limit_frame, text="Catalog Products to Extract:").pack(side='left')
        self.catalog_limit_var = tk.StringVar(value="2")
        catalog_spinbox = ttk.Spinbox(
            catalog_limit_frame,
            from_=1,
            to=20,
            textvariable=self.catalog_limit_var,
            width=5
        )
        catalog_spinbox.pack(side='left', padx=5)
        ttk.Label(catalog_limit_frame, text="(1-20 products)").pack(side='left', padx=5)
        
        # Original scraper limit (categories)
        original_limit_frame = ttk.Frame(limit_frame)
        original_limit_frame.pack(fill='x', pady=2)
        
        ttk.Label(original_limit_frame, text="Original Categories to Process:").pack(side='left')
        self.original_limit_var = tk.StringVar(value="1")
        original_spinbox = ttk.Spinbox(
            original_limit_frame,
            from_=1,
            to=13,
            textvariable=self.original_limit_var,
            width=5
        )
        original_spinbox.pack(side='left', padx=5)
        ttk.Label(original_limit_frame, text="(1-13 categories)").pack(side='left', padx=5)
        
        # Browser Settings
        self.browser_settings = BrowserSettings(self, self.settings)
        self.browser_settings.pack(fill='x', pady=5)
        
        # Control Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=10)
        
        self.start_button = ttk.Button(
            button_frame,
            text="🚀 Start Scraping",
            command=self.start_scraping
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹ Stop Scraping",
            command=self.stop_scraping,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        self.test_button = ttk.Button(
            button_frame,
            text="🧪 Test Navigation",
            command=self.test_navigation
        )
        self.test_button.pack(side='left', padx=5)
        
        # Quick Actions
        quick_frame = ttk.Frame(self)
        quick_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            quick_frame,
            text="🔄 Switch Scraper",
            command=self.switch_scraper
        ).pack(side='left', padx=5)
        
        ttk.Button(
            quick_frame,
            text="📊 Show Results",
            command=self.show_results
        ).pack(side='left', padx=5)
        
        # Status and Progress
        status_frame = ttk.LabelFrame(self, text="Status", padding="5")
        status_frame.pack(fill='x', pady=5)
        
        self.status_var = tk.StringVar(value="Ready to start scraping")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=2)
        
        # Product Count
        count_frame = ttk.Frame(status_frame)
        count_frame.pack(fill='x', pady=2)
        
        ttk.Label(count_frame, text="Extracted Products:").pack(side='left')
        self.product_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.product_count_var, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        
        # Bind scraper type change
        self.scraper_type_var.trace('w', self._on_scraper_type_changed)
        self._on_scraper_type_changed()
    
    def _on_scraper_type_changed(self, *args):
        """Handle scraper type change"""
        scraper_type = self.scraper_type_var.get()
        
        if scraper_type == "catalog":
            self.country_frame.pack_forget()
            self.status_var.set("Catalog scraper selected - extracts from wilo.com/katalog")
        else:
            self.country_frame.pack(fill='x', pady=5, before=self.browser_settings)
            self.status_var.set("Original scraper selected - extracts from select.wilo.com")
    
    def set_progress_callback(self, callback):
        """Set progress callback"""
        self.progress_callback = callback
    
    def set_products_callback(self, callback):
        """Set products callback"""
        self.products_callback = callback
    
    def start_scraping(self):
        """Start the appropriate scraper"""
        if self.is_scraping:
            return
        
        try:
            scraper_type = self.scraper_type_var.get()
            
            # Update browser settings
            browser_settings = self.browser_settings.get_settings()
            self.settings.headless_mode = browser_settings['headless_mode']
            self.settings.browser_timeout = browser_settings['browser_timeout']
            self.settings.page_load_delay = browser_settings['page_load_delay']
            
            # Update UI
            self.is_scraping = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress_bar.start()
            
            if scraper_type == "catalog":
                self._start_catalog_scraping()
            else:
                self._start_original_scraping()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scraping: {e}")
            self._reset_ui()
    
    def _start_catalog_scraping(self):
        """Start catalog scraping"""
        try:
            max_products = int(self.catalog_limit_var.get())
            
            self.catalog_scraper = WiloCatalogScraper(self.settings)
            self.catalog_scraper.set_progress_callback(self._update_progress)
            self.catalog_scraper.set_products_callback(self._add_product)
            
            self.status_var.set(f"Starting catalog scraping (max {max_products} products)...")
            
            # Start in separate thread
            thread = threading.Thread(target=self._catalog_scraping_worker, args=(max_products,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start catalog scraping: {e}")
            self._reset_ui()
    
    def _start_original_scraping(self):
        """Start original scraping"""
        try:
            country_key = self.country_selector.get_selected_country_key()
            max_categories = int(self.original_limit_var.get())
            
            self.original_scraper = WiloScraper(self.settings)
            self.original_scraper.set_progress_callback(self._update_progress)
            self.original_scraper.set_products_callback(self._add_product)
            
            self.status_var.set(f"Starting original scraping (max {max_categories} categories)...")
            
            # Start in separate thread
            thread = threading.Thread(target=self._original_scraping_worker, args=(country_key, max_categories))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start original scraping: {e}")
            self._reset_ui()
    
    def _catalog_scraping_worker(self, max_products):
        """Worker thread for catalog scraping"""
        try:
            products = self.catalog_scraper.start_scraping(max_products)
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.after(0, self._on_scraping_completed, len(products), "catalog")
            
        except Exception as e:
            self.after(0, self._on_scraping_failed, str(e))
    
    def _original_scraping_worker(self, country_key, max_categories):
        """Worker thread for original scraping"""
        try:
            products = self.original_scraper.start_scraping(country_key)
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.after(0, self._on_scraping_completed, len(products), "original")
            
        except Exception as e:
            self.after(0, self._on_scraping_failed, str(e))
    
    def _update_progress(self, message, start_progress=False, stop_progress=False):
        """Update progress display"""
        self.status_var.set(message)
        
        if self.progress_callback:
            self.progress_callback(message, start_progress, stop_progress)
    
    def _add_product(self, product_data):
        """Add product to results"""
        self.scraped_products.append(product_data)
        self.product_count_var.set(str(len(self.scraped_products)))
        
        if self.products_callback:
            self.products_callback(product_data)
    
    def _on_scraping_completed(self, product_count, scraper_type):
        """Handle scraping completion"""
        self._reset_ui()
        
        scraper_name = "Catalog" if scraper_type == "catalog" else "Original"
        self.status_var.set(f"{scraper_name} scraping completed! Found {product_count} products")
        
        messagebox.showinfo(
            "Scraping Complete", 
            f"✅ {scraper_name} scraping completed!\n\n"
            f"Found {product_count} new products\n"
            f"Total products: {len(self.scraped_products)}"
        )
    
    def _on_scraping_failed(self, error_message):
        """Handle scraping failure"""
        self._reset_ui()
        self.status_var.set("Scraping failed")
        messagebox.showerror("Error", f"❌ Scraping failed: {error_message}")
    
    def _reset_ui(self):
        """Reset UI after scraping"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
    
    def stop_scraping(self):
        """Stop current scraping"""
        if self.catalog_scraper:
            self.catalog_scraper.stop()
        if self.original_scraper:
            self.original_scraper.stop()
        
        self.status_var.set("Stopping scraping...")
        self._reset_ui()
    
    def test_navigation(self):
        """Test navigation for selected scraper"""
        try:
            scraper_type = self.scraper_type_var.get()
            
            self.status_var.set("Testing navigation...")
            
            if scraper_type == "catalog":
                test_scraper = WiloCatalogScraper(self.settings)
                test_scraper.set_progress_callback(self._update_progress)
            else:
                test_scraper = WiloScraper(self.settings)
                test_scraper.set_progress_callback(self._update_progress)
            
            # Run test in separate thread
            thread = threading.Thread(target=self._test_navigation_worker, args=(test_scraper,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Navigation test failed: {e}")
    
    def _test_navigation_worker(self, test_scraper):
        """Worker for navigation test"""
        try:
            success = test_scraper.test_navigation()
            self.after(0, self._on_navigation_test_completed, success)
        except Exception as e:
            self.after(0, self._on_navigation_test_failed, str(e))
    
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
    
    def switch_scraper(self):
        """Switch between scrapers"""
        current = self.scraper_type_var.get()
        new_scraper = "original" if current == "catalog" else "catalog"
        self.scraper_type_var.set(new_scraper)
        
        scraper_name = "Catalog" if new_scraper == "catalog" else "Original"
        self.status_var.set(f"Switched to {scraper_name} scraper")
    
    def show_results(self):
        """Show current results"""
        if not self.scraped_products:
            messagebox.showinfo("No Results", "No products have been scraped yet.")
            return
        
        # Create results window
        results_window = tk.Toplevel(self)
        results_window.title("Scraping Results")
        results_window.geometry("800x600")
        
        # Results text
        text_frame = ttk.Frame(results_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        results_text = tk.Text(text_frame, wrap='word')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=results_text.yview)
        results_text.configure(yscrollcommand=scrollbar.set)
        
        results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Display results
        results_text.insert('1.0', f"=== SCRAPING RESULTS ({len(self.scraped_products)} products) ===\n\n")
        
        for i, product in enumerate(self.scraped_products, 1):
            results_text.insert('end', f"{i}. {product.get('name', 'Unknown')}\n")
            results_text.insert('end', f"   Source: {product.get('source', 'unknown')}\n")
            results_text.insert('end', f"   Category: {product.get('category', 'Unknown')}\n")
            if product.get('short_description'):
                desc = product['short_description'][:100] + "..." if len(product['short_description']) > 100 else product['short_description']
                results_text.insert('end', f"   Description: {desc}\n")
            results_text.insert('end', "\n")
        
        results_text.config(state='disabled')
    
    def get_scraped_products(self):
        """Get all scraped products"""
        return self.scraped_products
    
    def clear_results(self):
        """Clear all scraped products"""
        self.scraped_products.clear()
        self.product_count_var.set("0")
        self.status_var.set("Results cleared")
'''
    
    with open('gui/widgets/enhanced_scraper_controller.py', 'w') as f:
        f.write(controller_content)
    
    print("✅ Created gui/widgets/enhanced_scraper_controller.py")

def main():
    """Main function to create all files"""
    print("🚀 Creating Enhanced Wilo Scraper with Dual Support")
    print("=" * 60)
    
    # Create the catalog scraper
    create_catalog_scraper()
    
    # Update main window
    create_enhanced_main_window()
    
    # Create enhanced controller
    create_enhanced_controller()
    
    print("\n✅ Enhanced Wilo Scraper Setup Complete!")
    print("\nFiles Created:")
    print("• scraper/wilo_catalog_scraper.py - New catalog scraper")
    print("• gui/main_window.py - Updated main window")
    print("• gui/widgets/enhanced_scraper_controller.py - Enhanced controller")
    
    print("\nWhat's New:")
    print("• 🆕 New catalog scraper for wilo.com/katalog")
    print("• 📊 Original select.wilo.com scraper (existing)")
    print("• 🎛️ Product limit controls (2 products default for catalog)")
    print("• 🖼️ Enhanced image and video extraction")
    print("• 📝 Short + long description extraction")
    print("• ✨ Advantages/benefits extraction")
    print("• 🔄 Switch between scrapers easily")
    print("• 📈 Real-time statistics and progress")
    
    print("\n🎯 Next Steps:")
    print("1. Run: python main.py")
    print("2. Choose 'New Catalog Scraper' option")
    print("3. Set number of products to extract (default: 2)")
    print("4. Click 'Start Scraping'")
    
    print("\n📝 The catalog scraper will:")
    print("• Extract card data (name, image, link)")
    print("• Click on each card to get product details")
    print("• Extract all images/videos from product page")
    print("• Extract short description from left side")
    print("• Extract 'Ihre Vorteile' section")
    print("• Extract long descriptions")
    print("• Build comprehensive Shopify-ready descriptions")

if __name__ == "__main__":
    main()