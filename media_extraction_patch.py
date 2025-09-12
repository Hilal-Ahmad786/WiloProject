def extract_carousel_media(self):
    """Extract ALL images and videos from carousel and thumbnails"""
    try:
        driver = self.browser_manager.get_driver()
        media_items = {'images': [], 'videos': [], 'all_media': []}
        
        # Extract from carousel items
        carousel_items = driver.find_elements(By.XPATH, "//div[@role='listitem']")
        for item in carousel_items:
            # Images
            imgs = item.find_elements(By.XPATH, ".//img[@src]")
            for img in imgs:
                src = img.get_attribute('src')
                if src:
                    if src.startswith('//'):
                        src = f"https:{src}"
                    if src not in media_items['images']:
                        media_items['images'].append(src)
                        media_items['all_media'].append({'type': 'image', 'url': src, 'source': 'carousel'})
            
            # Videos  
            iframes = item.find_elements(By.XPATH, ".//iframe[@src]")
            for iframe in iframes:
                src = iframe.get_attribute('src')
                if src and 'video' in src.lower():
                    if src.startswith('//'):
                        src = f"https:{src}"
                    if src not in media_items['videos']:
                        media_items['videos'].append(src)
                        media_items['all_media'].append({'type': 'video', 'url': src, 'source': 'carousel'})
        
        # Extract thumbnails
        thumbs = driver.find_elements(By.XPATH, "//div[contains(@class, 'cl-image-preview')]//img[@src]")
        for img in thumbs:
            src = img.get_attribute('src')
            if src:
                if src.startswith('//'):
                    src = f"https:{src}"
                if src not in media_items['images']:
                    media_items['images'].append(src)
                    media_items['all_media'].append({'type': 'image', 'url': src, 'source': 'thumbnail'})
        
        self.logger.info(f"Extracted {len(media_items['images'])} images and {len(media_items['videos'])} videos")
        return media_items
    except Exception as e:
        self.logger.error(f"Failed to extract media: {e}")
        return {'images': [], 'videos': [], 'all_media': []}
