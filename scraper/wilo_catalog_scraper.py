"""
Enhanced Wilo Catalog Scraper with Produktauswahl navigation and table extraction
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
    """Enhanced catalog scraper for Wilo products"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        self.progress_callback = None
        self.products_callback = None
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
            
            if not self.browser_manager.setup_driver():
                raise Exception("Failed to setup browser")
                
            driver = self.browser_manager.get_driver()
            
            if self.progress_callback:
                self.progress_callback("Navigating to Wilo catalog page...")
            
            self.logger.info("Navigating to Wilo catalog page...")
            driver.get(self.catalog_url)
            time.sleep(5)
            
            self.browser_manager.take_screenshot("catalog_step1_initial_page.png")
            
            if self.progress_callback:
                self.progress_callback("Finding product cards...")
                
            all_products = self.extract_products_from_cards(max_products)
            
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
    
    def extract_products_from_cards(self, max_products):
        """Extract products from card elements"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            
            time.sleep(5)
            
            card_selectors = [
                "//div[contains(@class, 'card cl-overview h-100 rebrush')]",
                "//div[contains(@class, 'card') and contains(@class, 'cl-overview')]"
            ]
            
            all_products = []
            
            for i in range(max_products):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Processing product card {i+1}/{max_products}")
                
                try:
                    self.logger.info(f"=== PROCESSING CARD {i+1} ===")
                    
                    # Enhanced card finding with better debugging
                    cards = []
                    current_url = driver.current_url
                    self.logger.info(f"🌐 Current URL: {current_url}")
                    
                    # Verify we're on the catalog page
                    if not ("katalog" in current_url.lower() and "industrie/heizung" in current_url.lower()):
                        self.logger.warning(f"⚠️  Not on catalog page, navigating...")
                        driver.get(self.catalog_url)
                        time.sleep(5)
                        self.browser_manager.take_screenshot(f"catalog_navigation_fix_card_{i}.png")
                    
                    # Try to find cards with enhanced error handling
                    for selector_idx, selector in enumerate(card_selectors):
                        try:
                            self.logger.info(f"🔍 Trying selector {selector_idx + 1}: {selector}")
                            found_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, selector)))
                            if found_cards:
                                cards = found_cards
                                self.logger.info(f"✅ Found {len(cards)} cards with selector {selector_idx + 1}")
                                
                                # Verify we have enough cards
                                if len(cards) > i:
                                    self.logger.info(f"✅ Card {i+1} is available in the list")
                                    break
                                else:
                                    self.logger.warning(f"⚠️  Only {len(cards)} cards found, but need card {i+1}")
                                    
                        except TimeoutException:
                            self.logger.warning(f"⏰ Timeout with selector {selector_idx + 1}")
                            continue
                        except Exception as e:
                            self.logger.error(f"❌ Error with selector {selector_idx + 1}: {e}")
                            continue
                    
                    # Final validation
                    if not cards:
                        self.logger.error(f"❌ No cards found with any selector")
                        self.browser_manager.take_screenshot(f"no_cards_found_card_{i}.png")
                        break
                    
                    if len(cards) <= i:
                        self.logger.warning(f"❌ No card found at position {i+1} (found {len(cards)} total cards)")
                        self.browser_manager.take_screenshot(f"insufficient_cards_card_{i}.png")
                        
                        # Try scrolling down to load more cards
                        try:
                            self.logger.info("📜 Trying to scroll down to load more cards...")
                            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(3)
                            driver.execute_script("window.scrollTo(0, 0);")
                            time.sleep(2)
                            
                            # Try finding cards again after scroll
                            for selector in card_selectors:
                                try:
                                    refreshed_cards = driver.find_elements(By.XPATH, selector)
                                    if len(refreshed_cards) > i:
                                        cards = refreshed_cards
                                        self.logger.info(f"✅ After scrolling, found {len(cards)} cards")
                                        break
                                except:
                                    continue
                        except Exception as scroll_e:
                            self.logger.warning(f"Scroll attempt failed: {scroll_e}")
                        
                        if len(cards) <= i:
                            break
                    
                    card = cards[i]
                    self.logger.info(f"🎯 Selected card {i+1} for processing")
                    
                    # Extract card data
                    card_data = self.extract_card_data_safe(card, i)
                    
                    if card_data:
                        # Click and extract details
                        product_detail = self.get_product_details_safe(card, card_data, i)
                        
                        if product_detail:
                            all_products.append(product_detail)
                            
                            if self.products_callback:
                                self.products_callback(product_detail)
                            
                            self.logger.info(f"✅ Successfully extracted: {product_detail['name']}")
                        else:
                            self.logger.warning(f"❌ Failed to get details for card {i+1}")
                    else:
                        self.logger.warning(f"❌ Failed to extract card data for card {i+1}")
                    
                    # Add extra wait between cards to ensure proper navigation
                    if i < max_products - 1:  # Don't wait after the last card
                        self.logger.info(f"⏳ Waiting before processing next card...")
                        time.sleep(3)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing card {i+1}: {e}")
                    # Try to return to catalog page before continuing
                    try:
                        driver.get(self.catalog_url)
                        time.sleep(5)
                        self.logger.info("🔄 Returned to catalog page after error")
                    except Exception as nav_e:
                        self.logger.error(f"❌ Failed to return to catalog after error: {nav_e}")
                    continue
            
            self.logger.info(f"=== EXTRACTION COMPLETE ===")
            self.logger.info(f"Successfully processed {len(all_products)} out of {max_products} cards")
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from cards: {e}")
            return []
    
    def extract_card_data_safe(self, card, index):
        """Extract basic data from card"""
        try:
            product_name = f"Product {index + 1}"
            
            image_url = ""
            try:
                img_element = card.find_element(By.XPATH, ".//img")
                img_src = img_element.get_attribute('src')
                if img_src:
                    if img_src.startswith('//'):
                        image_url = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        image_url = f"https://wilo.com{img_src}"
                    else:
                        image_url = img_src
            except:
                self.logger.debug(f"Could not find image in card {index+1}")
            
            product_link = ""
            link_selectors = [
                ".//a[@class='stretched-link']",
                ".//a[contains(@class, 'stretched')]",
                ".//a[@href]"
            ]
            
            for selector in link_selectors:
                try:
                    link_element = card.find_element(By.XPATH, selector)
                    href = link_element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            product_link = f"https://wilo.com{href}"
                        else:
                            product_link = href
                        break
                except:
                    continue
            
            card_data = {
                'name': product_name,
                'card_image_url': image_url,
                'product_link': product_link,
                'card_index': index
            }
            
            self.logger.info(f"Extracted card data for position {index+1}")
            return card_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract card data: {e}")
            return {
                'name': f"Product {index + 1}",
                'card_image_url': '',
                'product_link': '',
                'card_index': index
            }
    
    def get_product_details_safe(self, card, card_data, index):
        """Click on card and extract product details"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Try clicking via link first
            clicked = False
            if card_data.get('product_link'):
                try:
                    link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                    driver.execute_script("arguments[0].click();", link_element)
                    self.logger.info(f"Clicked via link for card {index+1}")
                    clicked = True
                except Exception as e:
                    self.logger.warning(f"Link click failed: {e}")
            
            # If link click failed, try clicking the card itself
            if not clicked:
                try:
                    driver.execute_script("arguments[0].click();", card)
                    self.logger.info(f"Clicked directly on card {index+1}")
                    clicked = True
                except Exception as e:
                    self.logger.error(f"Direct card click failed: {e}")
            
            if not clicked:
                self.logger.error(f"Could not click card {index+1}")
                return None
            
            time.sleep(5)
            self.browser_manager.take_screenshot(f"catalog_product_{index}_page.png")
            
            product_details = self.extract_product_page_details(card_data)
            
            driver.back()
            time.sleep(3)
            
            return product_details
            
        except Exception as e:
            self.logger.error(f"Failed to get product details: {e}")
            return None
    
    def extract_product_page_details(self, card_data):
        """Extract detailed info from product page and navigate to Produktauswahl"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Extract media and descriptions from main product page first
            media_items = self.extract_all_media()
            short_description = self.extract_short_description()
            advantages = self.extract_advantages()
            long_description = self.extract_long_description()
            
            # Now navigate to Produktauswahl and extract table data
            table_data = self.navigate_to_produktauswahl_and_extract_tables()
            
            # Get real product name from H1 (but exclude it from the final description)
            real_product_name = ""
            try:
                h1_element = driver.find_element(By.XPATH, "//h1[@class='m-0']")
                real_product_name = h1_element.text.strip()
                self.logger.info(f"Extracted real name from H1: {real_product_name}")
            except:
                try:
                    h1_element = driver.find_element(By.XPATH, "//h1")
                    real_product_name = h1_element.text.strip()
                    self.logger.info(f"Extracted name from fallback H1: {real_product_name}")
                except:
                    real_product_name = f"Wilo Product {card_data.get('card_index', 0) + 1}"
                    self.logger.warning(f"Using fallback name: {real_product_name}")
            
            # Create comprehensive product object
            product = {
                'id': f"catalog_{card_data['card_index']+1}_{int(time.time())}",
                'name': real_product_name,
                'category': 'Industrie Heizung',
                'subcategory': 'Heizungspumpen',
                'source': 'catalog',
                'card_image_url': card_data['card_image_url'],
                'product_images': media_items['images'],
                'product_videos': media_items['videos'],
                'all_media': media_items['all_media'],
                'short_description': short_description,
                'advantages': advantages,
                'long_description': long_description,
                'full_description': self.build_full_description(short_description, advantages, long_description),
                'technical_specifications': table_data,
                'product_url': driver.current_url,
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'specifications': {
                    'brand': 'Wilo',
                    'series': real_product_name,
                    'application': 'Industrie Heizung',
                    'type': 'Heizungspumpe'
                },
                'price': 'Price on request',
                'currency': 'EUR',
                'country': 'Germany',
                'status': 'Catalog Product - Real Extraction'
            }
            
            # Debug logging
            self.logger.info(f"🔍 PRODUCT DEBUG for {real_product_name}:")
            self.logger.info(f"   Real name from H1: {real_product_name}")
            self.logger.info(f"   Short desc length: {len(short_description)} chars")
            self.logger.info(f"   Advantages count: {len(advantages)}")
            self.logger.info(f"   Product images: {len(media_items['images'])}")
            self.logger.info(f"   Technical tables: {len(table_data)}")
            
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to extract product details: {e}")
            return None

    def navigate_to_produktauswahl_and_extract_tables(self):
        """Navigate to Produktauswahl tab and extract table data from the selected product"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            table_data = []
            
            # Step 1: Click on Produktauswahl tab
            self.logger.info("Looking for Produktauswahl tab...")
            
            produktauswahl_selectors = [
                "//li[@class='nav-item']//a[contains(@href, '#range_productlist') and contains(text(), 'Produktauswahl')]",
                "//a[contains(@href, '#range_productlist')]",
                "//a[contains(text(), 'Produktauswahl')]"
            ]
            
            produktauswahl_clicked = False
            for selector in produktauswahl_selectors:
                try:
                    tab_element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab_element)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", tab_element)
                    self.logger.info("✅ Successfully clicked Produktauswahl tab")
                    produktauswahl_clicked = True
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to click Produktauswahl with selector {selector}: {e}")
                    continue
            
            if not produktauswahl_clicked:
                self.logger.warning("❌ Could not click Produktauswahl tab")
                return []
            
            time.sleep(3)
            self.browser_manager.take_screenshot("produktauswahl_table_page.png")
            
            # Step 2: Find the table and click on the first item
            self.logger.info("Looking for product table...")
            
            table_selectors = [
                "//table//tbody//tr[1]//td[1]//a",
                "//tbody//tr[1]//td[1]//a",
                "//tr[1]//td[1]//a"
            ]
            
            first_product_clicked = False
            selected_product_name = ""
            for selector in table_selectors:
                try:
                    first_product_link = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    selected_product_name = first_product_link.text.strip()
                    self.logger.info(f"✅ Found first product in table: {selected_product_name}")
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_product_link)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", first_product_link)
                    self.logger.info(f"✅ Successfully clicked on first product: {selected_product_name}")
                    first_product_clicked = True
                    break
                except Exception as e:
                    self.logger.warning(f"Failed to click first product with selector {selector}: {e}")
                    continue
            
            if not first_product_clicked:
                self.logger.warning("❌ Could not click on first product in table")
                return []
            
            time.sleep(5)
            self.browser_manager.take_screenshot("product_detail_tables_page.png")
            
            # Step 3: Extract all table data from the new page
            self.logger.info("🔍 Starting table data extraction from product detail page...")
            
            # Look for tables with technical specifications
            table_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'cl-card-table-simple')]//table[@class='cl-table-simple']")
            
            self.logger.info(f"📊 Found {len(table_containers)} tables on the page")
            
            if len(table_containers) == 0:
                self.logger.warning("❌ No tables found with the expected selectors")
                # Try alternative selectors
                alternative_selectors = [
                    "//table",
                    "//div[contains(@class, 'table')]//table",
                    "//div[contains(@class, 'row')]//table"
                ]
                
                for alt_selector in alternative_selectors:
                    try:
                        alt_tables = driver.find_elements(By.XPATH, alt_selector)
                        if alt_tables:
                            self.logger.info(f"📊 Found {len(alt_tables)} tables with alternative selector: {alt_selector}")
                            table_containers = alt_tables[:4]  # Limit to first 4 tables
                            break
                    except Exception as e:
                        continue
            
            for i, table in enumerate(table_containers):
                try:
                    table_dict = {}
                    
                    self.logger.info(f"🔍 Processing table {i+1}/{len(table_containers)}...")
                    
                    # Extract table header
                    header_elements = table.find_elements(By.XPATH, ".//thead//th")
                    if header_elements:
                        table_title = header_elements[0].text.strip()
                        table_dict['title'] = table_title
                        self.logger.info(f"📋 Table title: '{table_title}'")
                    else:
                        table_dict['title'] = f"Technical Data Table {i+1}"
                        self.logger.info(f"📋 No header found, using default title: {table_dict['title']}")
                    
                    # Extract table rows
                    rows = table.find_elements(By.XPATH, ".//tbody//tr")
                    table_rows = {}
                    
                    self.logger.info(f"📝 Found {len(rows)} rows in table")
                    
                    for row_idx, row in enumerate(rows):
                        try:
                            cells = row.find_elements(By.XPATH, ".//td")
                            if len(cells) >= 2:
                                key = cells[0].text.strip()
                                value = cells[1].text.strip()
                                if key and value:
                                    table_rows[key] = value
                                    self.logger.debug(f"   Row {row_idx+1}: '{key}' = '{value}'")
                                else:
                                    self.logger.debug(f"   Row {row_idx+1}: Empty key or value")
                            else:
                                self.logger.debug(f"   Row {row_idx+1}: Less than 2 cells ({len(cells)} cells)")
                        except Exception as e:
                            self.logger.warning(f"   Error processing row {row_idx+1}: {e}")
                            continue
                    
                    table_dict['data'] = table_rows
                    table_dict['product_name'] = selected_product_name
                    table_data.append(table_dict)
                    
                    self.logger.info(f"✅ Successfully extracted {len(table_rows)} data rows from table: '{table_dict['title']}'")
                    
                    # Log first few entries for debugging
                    if table_rows:
                        first_entries = list(table_rows.items())[:3]
                        self.logger.info(f"   Sample data: {first_entries}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error extracting table {i+1}: {e}")
                    continue
            
            # Final summary
            total_data_points = sum(len(table['data']) for table in table_data)
            self.logger.info(f"🎉 TABLE EXTRACTION COMPLETE!")
            self.logger.info(f"   ✅ Successfully extracted {len(table_data)} tables")
            self.logger.info(f"   ✅ Total data points: {total_data_points}")
            self.logger.info(f"   📊 Tables found: {[table['title'] for table in table_data]}")
            
            if len(table_data) == 0:
                self.logger.warning("❌ WARNING: No table data was extracted!")
                # Take a screenshot for debugging
                self.browser_manager.take_screenshot("no_tables_found_debug.png")
            
            return table_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to navigate to Produktauswahl and extract tables: {e}")
            self.browser_manager.take_screenshot("table_extraction_error.png")
            return []

    def extract_all_media(self):
        """Extract images/videos by clicking thumbnails; if none, capture a single product image."""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 10)
            media_items = {'images': [], 'videos': [], 'all_media': []}

            def _norm(url: str) -> str:
                if not url:
                    return url
                url = url.strip()
                if url.startswith('//'):
                    return f"https:{url}"
                if url.startswith('/'):
                    return f"https://wilo.com{url}"
                return url

            def _get_active_media_src():
                """Return (type, src) from the active main slide: 'image' or 'video'."""
                try:
                    active = driver.find_element(
                        By.XPATH,
                        "//div[contains(@class,'carousel-inner')]"
                        "//div[contains(@class,'carousel-item') and contains(@class,'active')]"
                    )
                except Exception:
                    return None, None

                # Prefer image in active slide
                try:
                    img = active.find_element(By.XPATH, ".//img[@src or @data-src or @srcset]")
                    src = img.get_attribute('src') or img.get_attribute('data-src') or ""
                    if not src:
                        srcset = img.get_attribute('srcset') or ""
                        if srcset:
                            parts = [p.strip() for p in srcset.split(',') if p.strip()]
                            if parts:
                                src = parts[-1].split(' ')[0]
                    return "image", _norm(src)
                except Exception:
                    pass

                # Fallback: iframe video in active slide
                try:
                    iframe = active.find_element(By.XPATH, ".//iframe[@src]")
                    vsrc = iframe.get_attribute('src') or ""
                    return "video", _norm(vsrc)
                except Exception:
                    pass

                return None, None

            # 1) Find and iterate thumbnails
            thumbs = driver.find_elements(
                By.XPATH,
                "//div[contains(@class,'cl-image-preview')][.//img]"
            )
            self.logger.info(f"Found {len(thumbs)} thumbnail tiles")

            if thumbs:
                # Initial main src (to detect change after clicking a thumb)
                _, prev_src = _get_active_media_src()

                for idx, tile in enumerate(thumbs, start=1):
                    try:
                        # Scroll into view (center) to avoid intercept issues
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tile)
                        time.sleep(0.1)

                        # Click thumbnail (try standard click first, then JS)
                        try:
                            tile.click()
                        except Exception:
                            driver.execute_script("arguments[0].click();", tile)

                        # Wait until the active media changes src or becomes available
                        def _changed(drv):
                            t, s = _get_active_media_src()
                            if s and s != (prev_src or ""):
                                return (t, s)
                            return False

                        try:
                            result = WebDriverWait(driver, 8).until(_changed)
                            new_type, new_src = result
                        except TimeoutException:
                            # If main didn't update, fall back to the thumb's own img URL
                            try:
                                timg = tile.find_element(By.XPATH, ".//img[@src or @data-src or @srcset]")
                                t_src = timg.get_attribute('src') or timg.get_attribute('data-src') or ""
                                if not t_src:
                                    t_ss = timg.get_attribute('srcset') or ""
                                    if t_ss:
                                        parts = [p.strip() for p in t_ss.split(',') if p.strip()]
                                        if parts:
                                            t_src = parts[-1].split(' ')[0]
                                new_type, new_src = "image", _norm(t_src)
                            except Exception:
                                new_type, new_src = None, None

                        # Record media
                        if new_src:
                            if new_type == "video":
                                if new_src not in media_items['videos']:
                                    media_items['videos'].append(new_src)
                                    media_items['all_media'].append({
                                        'type': 'video',
                                        'url': new_src,
                                        'title': f'Product Video {len(media_items["videos"])}',
                                        'source': 'carousel'
                                    })
                                    self.logger.info(f"[thumb {idx}] Added video: {new_src}")
                            else:
                                # Accept images including png/jpg/webp/gif; allow others too if provided
                                if new_src not in media_items['images']:
                                    media_items['images'].append(new_src)
                                    media_items['all_media'].append({
                                        'type': 'image',
                                        'url': new_src,
                                        'alt': f'Carousel Image {len(media_items["images"])}',
                                        'source': 'carousel'
                                    })
                                    self.logger.info(f"[thumb {idx}] Added image: {new_src}")

                            prev_src = new_src  # update baseline

                    except Exception as e:
                        self.logger.warning(f"Error processing thumbnail {idx}: {e}")
                        continue

            # 2) If no thumbnails or none yielded media, capture a single main product image
            if not media_items['images'] and not media_items['videos']:
                self.logger.info("No media via thumbnails; trying to capture a single main product image")
                try:
                    # Try the active carousel image first
                    mtype, msrc = _get_active_media_src()
                    if msrc and mtype == "image":
                        media_items['images'].append(msrc)
                        media_items['all_media'].append({
                            'type': 'image',
                            'url': msrc,
                            'alt': 'Main Product Image',
                            'source': 'carousel'
                        })
                        self.logger.info(f"[single] Added main product image: {msrc}")
                    elif msrc and mtype == "video":
                        media_items['videos'].append(msrc)
                        media_items['all_media'].append({
                            'type': 'video',
                            'url': msrc,
                            'title': 'Product Video 1',
                            'source': 'carousel'
                        })
                        self.logger.info(f"[single] Added main product video: {msrc}")
                    else:
                        # As a last resort, any large image inside the carousel area
                        try:
                            any_img = driver.find_element(
                                By.XPATH,
                                "//div[contains(@class,'carousel-inner')]//img[@src or @data-src or @srcset]"
                            )
                            src = any_img.get_attribute('src') or any_img.get_attribute('data-src') or ""
                            if not src:
                                ss = any_img.get_attribute('srcset') or ""
                                if ss:
                                    parts = [p.strip() for p in ss.split(',') if p.strip()]
                                    if parts:
                                        src = parts[-1].split(' ')[0]
                            src = _norm(src)
                            if src:
                                media_items['images'].append(src)
                                media_items['all_media'].append({
                                    'type': 'image',
                                    'url': src,
                                    'alt': 'Product Image',
                                    'source': 'carousel'
                                })
                                self.logger.info(f"[fallback single] Added product image: {src}")
                        except Exception:
                            pass
                except Exception as e:
                    self.logger.error(f"Error capturing single product image: {e}")

            self.logger.info(
                f"Media extraction complete - Images: {len(media_items['images'])}, Videos: {len(media_items['videos'])}"
            )
            return media_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract media: {e}")
            return {'images': [], 'videos': [], 'all_media': []}

    def extract_short_description(self):
        """Extract short description (excluding product heading)"""
        try:
            driver = self.browser_manager.get_driver()
            
            short_desc_selectors = [
                "//div[@class='pl-md-8 col']//h3",
                "//div[@class='pl-md-8 col']//div//p",
                "//div[contains(@class, 'pl-md-8')]//h3",
                "//div[contains(@class, 'pl-md-8')]//p"
            ]
            
            short_description_parts = []
            
            # Get the product name to exclude it
            product_heading = ""
            try:
                h1_element = driver.find_element(By.XPATH, "//h1")
                product_heading = h1_element.text.strip()
            except:
                pass
            
            for selector in short_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        # Skip if this text is the product heading
                        if text and len(text) > 10 and text != product_heading:
                            short_description_parts.append(text)
                except:
                    continue
            
            short_description = " ".join(short_description_parts)
            self.logger.info(f"Extracted short description: {len(short_description)} characters")
            return short_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract short description: {e}")
            return ""
    
    def extract_advantages(self):
        """Extract advantages list"""
        try:
            driver = self.browser_manager.get_driver()
            
            advantages_selectors = [
                "//div[@class='cl-your-advantages']//ul//li",
                "//div[contains(@class, 'cl-your-advantages')]//li",
                "//h3[contains(text(), 'Ihre Vorteile')]//following-sibling::div//li"
            ]
            
            advantages = []
            
            for selector in advantages_selectors:
                try:
                    li_elements = driver.find_elements(By.XPATH, selector)
                    if li_elements:
                        for li in li_elements:
                            text = li.text.strip()
                            if text and len(text) > 20:
                                advantages.append(text)
                        break
                except:
                    continue
            
            self.logger.info(f"Extracted {len(advantages)} advantages")
            return advantages
            
        except Exception as e:
            self.logger.error(f"Failed to extract advantages: {e}")
            return []
    
    def extract_long_description(self, product_name=""):
        """Extract long description"""
        try:
            driver = self.browser_manager.get_driver()
            
            long_desc_selectors = [
                "//div[contains(@class, 'text-module')]//div[contains(@class, 'text-wrapper')]//p",
                "//div[contains(@class, 'page-module')]//div[contains(@class, 'text-wrapper')]"
            ]
            
            long_description_parts = []
            
            for selector in long_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 50:
                            # Clean up the text
                            text = re.sub(r'\s+', ' ', text)
                            
                            # Skip unwanted content
                            skip_text = any([
                                'über wilo' in text.lower(),
                                'wilo ist ein' in text.lower(),
                                text == product_name,
                                text.lower().startswith(product_name.lower().split()[0]) if product_name else False
                            ])
                            
                            if not skip_text and text not in long_description_parts:
                                long_description_parts.append(text)
                except:
                    continue
            
            long_description = "\n\n".join(long_description_parts)
            self.logger.info(f"Extracted long description: {len(long_description)} characters")
            return long_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract long description: {e}")
            return ""
    
    def build_full_description(self, short_desc, advantages, long_desc):
        """Build comprehensive description (excluding product heading and 'Über Wilo' section)"""
        try:
            html_parts = []
            
            if short_desc:
                html_parts.append(f"<div class='product-intro'>{short_desc}</div>")
            
            if advantages:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    html_parts.append(f"<li>{advantage}</li>")
                html_parts.append("</ul>")
            
            if long_desc:
                paragraphs = long_desc.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # Skip paragraphs that contain "Über Wilo" content
                        if "über wilo" in paragraph.lower() or "wilo ist ein" in paragraph.lower():
                            continue
                        html_parts.append(f"<p>{paragraph.strip()}</p>")
            
            # Note: Removed the "Über Wilo" section as requested
            
            return "\n".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to build description: {e}")
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
            
            if "wilo.com" in driver.current_url and "katalog" in driver.current_url.lower():
                self.logger.info("Navigation test successful")
                if self.progress_callback:
                    self.progress_callback("Navigation test successful!", stop_progress=True)
                return True
            else:
                self.logger.error("Navigation test failed")
                if self.progress_callback:
                    self.progress_callback("Navigation test failed", stop_progress=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Navigation test failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Navigation test failed: {e}", stop_progress=True)
            return False
        finally:
            self.browser_manager.quit()
    
    def stop(self):
        """Stop scraping"""
        self.logger.info("Stopping catalog scraper...")
        self.is_running = False
        if self.progress_callback:
            self.progress_callback("Catalog scraping stopped", stop_progress=True)