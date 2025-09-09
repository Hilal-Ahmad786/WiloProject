"""
Screenshot management utilities
"""

import os
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

class ScreenshotManager:
    """Manages debug screenshots"""
    
    def __init__(self, screenshots_dir: str = "logs/screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger(__name__)
    
    def take_screenshot(self, driver, name: str) -> str:
        """Take a screenshot with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.png"
            filepath = self.screenshots_dir / filename
            
            driver.save_screenshot(str(filepath))
            self.logger.info(f"Screenshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def cleanup_old_screenshots(self, days: int = 7):
        """Remove screenshots older than specified days"""
        try:
            import time
            
            current_time = time.time()
            cutoff_time = current_time - (days * 24 * 60 * 60)
            
            removed_count = 0
            for screenshot in self.screenshots_dir.glob("*.png"):
                if screenshot.stat().st_mtime < cutoff_time:
                    screenshot.unlink()
                    removed_count += 1
            
            if removed_count > 0:
                self.logger.info(f"Removed {removed_count} old screenshots")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup screenshots: {e}")
