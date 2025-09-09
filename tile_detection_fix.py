#!/usr/bin/env python3
"""
Fix tile detection with broader selectors
"""

def fix_tile_detection():
    """Update the _navigate_to_pump_selection method with better tile detection"""
    
    # Read current scraper file
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # New _navigate_to_pump_selection method
    new_method = '''    def _navigate_to_pump_selection(self):
        """Navigate to hydraulic pump selection using broad tile detection"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 20)
            
            self.logger.info("Looking for Hydraulische Pumpenauswahl tile...")
            
            # Wait a bit for page to fully load after country selection
            time.sleep(5)
            
            # Take screenshot for debugging
            self.browser_manager.take_screenshot("step4_looking_for_tiles.png")
            
            # Strategy 1: Look for any text containing "Hydraulische" or "Pumpen"
            pump_keywords = ["Hydraulische", "Pumpen", "pump", "selection", "auswahl"]
            
            tile_element = None
            
            # Try to find any clickable element with pump-related text
            for keyword in pump_keywords:
                try:
                    # Look for elements containing the keyword (case insensitive)
                    elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]")
                    
                    for element in elements:
                        if element.is_displayed():
                            # Check if this element or its parent is clickable
                            clickable_ancestor = element
                            for _ in range(5):  # Go up max 5 levels
                                try:
                                    if clickable_ancestor.tag_name in ['a', 'button', 'div'] and clickable_ancestor.is_enabled():
                                        tile_element = clickable_ancestor
                                        self.logger.info(f"Found tile with keyword '{keyword}': {element.text[:50]}")
                                        break
                                    clickable_ancestor = clickable_ancestor.find_element(By.XPATH, "./..")
                                except:
                                    break
                            if tile_element:
                                break
                    if tile_element:
                        break
                except Exception as e:
                    continue
            
            # Strategy 2: Look for common tile/button patterns
            if not tile_element:
                tile_selectors = [
                    "//div[contains(@class, 'tile')]",
                    "//div[contains(@class, 'button')]",
                    "//div[contains(@class, 'btn')]",
                    "//td[contains(@class, 'tile')]",
                    "//a[contains(@class, 'tile')]",
                    "//div[contains(@id, 'tile')]",
                    "//div[contains(@id, 'btn')]"
                ]
                
                for selector in tile_selectors:
                    try:
                        elements = driver.find_elements(By.XPATH, selector)
                        for element in elements:
                            if element.is_displayed() and element.text:
                                element_text = element.text.lower()
                                if any(keyword.lower() in element_text for keyword in pump_keywords):
                                    tile_element = element
                                    self.logger.info(f"Found tile with selector '{selector}': {element.text[:50]}")
                                    break
                        if tile_element:
                            break
                    except:
                        continue
            
            # Strategy 3: Look for any large clickable elements (tiles are usually big)
            if not tile_element:
                try:
                    large_elements = driver.find_elements(By.XPATH, "//div[@style and contains(@style, 'width') and contains(@style, 'height')] | //td[@style and contains(@style, 'width') and contains(@style, 'height')]")
                    
                    for element in large_elements:
                        try:
                            if element.is_displayed() and element.size['width'] > 100 and element.size['height'] > 100:
                                if element.text and any(keyword.lower() in element.text.lower() for keyword in pump_keywords):
                                    tile_element = element
                                    self.logger.info(f"Found large tile element: {element.text[:50]}")
                                    break
                        except:
                            continue
                except:
                    pass
            
            # Strategy 4: Debug - show all available clickable elements
            if not tile_element:
                self.logger.info("No pump tile found, showing all available clickable elements...")
                try:
                    clickable_elements = driver.find_elements(By.XPATH, "//a | //button | //div[@onclick] | //div[contains(@class, 'clickable')] | //div[contains(@class, 'button')] | //div[contains(@class, 'tile')]")
                    
                    available_elements = []
                    for element in clickable_elements[:20]:  # Limit to first 20
                        try:
                            if element.is_displayed() and element.text.strip():
                                available_elements.append(element.text.strip()[:50])
                        except:
                            continue
                    
                    self.logger.info(f"Available clickable elements: {available_elements}")
                    
                    # Try to click the first element that might be a pump-related tile
                    for element in clickable_elements:
                        try:
                            if element.is_displayed() and element.text:
                                element_text = element.text.lower()
                                if 'pump' in element_text or 'hydraul' in element_text or 'select' in element_text:
                                    tile_element = element
                                    self.logger.info(f"Trying element with text: {element.text[:50]}")
                                    break
                        except:
                            continue
                            
                except Exception as e:
                    self.logger.error(f"Error during debugging: {e}")
            
            # Try to click the found element
            if tile_element:
                try:
                    # Scroll to element
                    driver.execute_script("arguments[0].scrollIntoView();", tile_element)
                    time.sleep(2)
                    
                    # Try JavaScript click first
                    try:
                        driver.execute_script("arguments[0].click();", tile_element)
                        self.logger.info("Successfully clicked pump selection tile with JavaScript")
                    except:
                        tile_element.click()
                        self.logger.info("Successfully clicked pump selection tile with regular click")
                    
                    # Wait for navigation
                    time.sleep(self.settings.page_load_delay)
                    
                    # Take screenshot after tile click
                    self.browser_manager.take_screenshot("step5_after_tile_click.png")
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Failed to click tile element: {e}")
                    return False
            else:
                self.logger.error("Could not find any pump selection tile")
                
                # Take final screenshot for debugging
                self.browser_manager.take_screenshot("step4_no_tiles_found.png")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to navigate to pump selection: {e}")
            return False'''
    
    # Replace the old method with the new one
    import re
    pattern = r'def _navigate_to_pump_selection\(self\):.*?(?=def |\Z)'
    
    new_content = re.sub(pattern, new_method + '\n\n    ', content, flags=re.DOTALL)
    
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated tile detection with broader search strategies")

def main():
    print("🔧 Fixing Tile Detection")
    print("=" * 25)
    
    fix_tile_detection()
    
    print("\n✅ Tile detection improved!")
    print("Now it will:")
    print("- Look for any text containing 'Hydraulische', 'Pumpen', etc.")
    print("- Check common tile/button CSS classes")
    print("- Find large clickable elements")
    print("- Show all available clickable elements for debugging")
    print("\n🎯 Try running:")
    print("python main.py")
    print("\nCheck the new screenshots:")
    print("- step4_looking_for_tiles.png")
    print("- step5_after_tile_click.png (if successful)")

if __name__ == "__main__":
    main()