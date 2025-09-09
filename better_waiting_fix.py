#!/usr/bin/env python3
"""
Fix the waiting logic for page loading
"""

def fix_waiting_logic():
    """Update the navigation method with better waiting"""
    
    # Read current file
    with open('scraper/wilo_scraper.py', 'r') as f:
        content = f.read()
    
    # New navigation method with better waiting
    new_navigation_method = '''    def _navigate_to_pump_selection(self):
        """Navigate to hydraulic pump selection with better waiting"""
        try:
            driver = self.browser_manager.get_driver()
            
            self.logger.info("Looking for Hydraulische Pumpenauswahl tile...")
            
            # Wait much longer for page to fully load after country selection
            self.logger.info("Waiting for page to fully load after country selection...")
            
            # Progressive waiting with status checks
            for wait_time in [5, 10, 15, 20, 25, 30]:
                self.logger.info(f"Waiting {wait_time} seconds for tiles to appear...")
                time.sleep(5)  # Wait 5 more seconds each iteration
                
                # Take screenshot to see current state
                self.browser_manager.take_screenshot(f"step4_wait_{wait_time}s.png")
                
                # Check if tiles are available now
                pump_keywords = ["Hydraulische", "Pumpen", "pump", "selection", "auswahl", "Pumpenauswahl"]
                tile_element = None
                
                # Strategy 1: Look for any text containing pump keywords
                for keyword in pump_keywords:
                    try:
                        elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]")
                        
                        for element in elements:
                            if element.is_displayed():
                                # Check if this element or its parent is clickable
                                clickable_ancestor = element
                                for _ in range(5):
                                    try:
                                        if clickable_ancestor.tag_name in ['a', 'button', 'div', 'td'] and clickable_ancestor.is_enabled():
                                            # Additional check: make sure it's not just random text
                                            element_text = element.text.strip()
                                            if len(element_text) > 10 and 'hydraul' in element_text.lower():
                                                tile_element = clickable_ancestor
                                                self.logger.info(f"Found tile with keyword '{keyword}': {element_text[:50]}")
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
                
                # Strategy 2: Look for common tile patterns
                if not tile_element:
                    tile_selectors = [
                        "//div[contains(@class, 'tile') and contains(text(), 'Hydraul')]",
                        "//div[contains(@class, 'button') and contains(text(), 'Hydraul')]",
                        "//td[contains(@class, 'tile') and contains(text(), 'Hydraul')]",
                        "//div[contains(@id, 'tile') and contains(text(), 'Hydraul')]",
                        "//div[contains(@id, 'btn') and contains(text(), 'Hydraul')]",
                        "//*[@class='tdCont tileButton']//span[contains(text(), 'Hydraul')]"
                    ]
                    
                    for selector in tile_selectors:
                        try:
                            elements = driver.find_elements(By.XPATH, selector)
                            for element in elements:
                                if element.is_displayed():
                                    # For tile selectors, get the clickable parent
                                    if 'span' in selector:
                                        # Get the tile container
                                        tile_element = element.find_element(By.XPATH, "./ancestor::div[@class='tdCont tileButton']")
                                    else:
                                        tile_element = element
                                    
                                    if tile_element:
                                        self.logger.info(f"Found tile with selector '{selector}': {element.text[:50]}")
                                        break
                            if tile_element:
                                break
                        except:
                            continue
                
                # Strategy 3: Show what's currently available for debugging
                if not tile_element:
                    self.logger.info(f"No tile found after {wait_time}s, checking available elements...")
                    try:
                        # Look for any clickable elements
                        clickable_elements = driver.find_elements(By.XPATH, "//a | //button | //div[@onclick] | //div[contains(@class, 'tile')] | //div[contains(@class, 'button')]")
                        
                        available_elements = []
                        for element in clickable_elements[:15]:  # Limit to first 15
                            try:
                                if element.is_displayed() and element.text.strip():
                                    text = element.text.strip()[:50]
                                    if len(text) > 5:  # Skip very short texts
                                        available_elements.append(text)
                            except:
                                continue
                        
                        self.logger.info(f"Available clickable elements: {available_elements}")
                        
                        # Try to find anything that might be pump-related
                        for element in clickable_elements:
                            try:
                                if element.is_displayed() and element.text:
                                    element_text = element.text.lower()
                                    pump_related_words = ['pump', 'hydraul', 'select', 'auswahl', 'wilo', 'system']
                                    if any(word in element_text for word in pump_related_words) and len(element.text.strip()) > 10:
                                        tile_element = element
                                        self.logger.info(f"Found potential pump element: {element.text[:50]}")
                                        break
                            except:
                                continue
                                
                    except Exception as e:
                        self.logger.error(f"Error during debugging: {e}")
                
                # If we found a tile, try to click it
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
                        
                        # Verify we're on a new page
                        time.sleep(3)
                        current_url = driver.current_url
                        self.logger.info(f"After tile click, current URL: {current_url}")
                        
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"Failed to click tile element: {e}")
                        # Continue waiting instead of failing
                        continue
                
                # If we've waited 30+ seconds, that should be enough
                if wait_time >= 30:
                    break
            
            # Final attempt: try to proceed anyway
            self.logger.error("Could not find pump selection tile after extended waiting")
            
            # Take final screenshot for debugging
            self.browser_manager.take_screenshot("step4_final_no_tiles.png")
            
            # Check if we're already on the right page somehow
            current_url = driver.current_url
            page_source = driver.page_source
            
            if 'pump' in page_source.lower() or 'hydraul' in page_source.lower():
                self.logger.info("Page seems to contain pump-related content, proceeding anyway")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to navigate to pump selection: {e}")
            return False'''
    
    # Replace the old method
    import re
    pattern = r'def _navigate_to_pump_selection\(self\):.*?(?=def |\Z)'
    
    new_content = re.sub(pattern, new_navigation_method + '\n\n    ', content, flags=re.DOTALL)
    
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Updated navigation with better waiting logic")

def main():
    print("🔧 Fixing Page Loading Wait Times")
    print("=" * 35)
    
    fix_waiting_logic()
    
    print("\n✅ Waiting logic improved!")
    print("Now the scraper will:")
    print("- Wait progressively: 5s, 10s, 15s, 20s, 25s, 30s")
    print("- Take screenshots at each wait interval")
    print("- Show available elements for debugging")
    print("- Try multiple strategies to find the tile")
    print("- Continue even if tile not found but page has pump content")
    print("\n🎯 Try running:")
    print("python main.py")
    print("\nCheck the new screenshots:")
    print("- step4_wait_5s.png, step4_wait_10s.png, etc.")
    print("- These will show how the page loads over time")

if __name__ == "__main__":
    main()