"""
File management utilities
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any
from utils.logger import get_logger

class FileManager:
    """Handles file operations for scraped data"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def export_to_json(self, data: List[Dict], filepath: str) -> bool:
        """Export data to JSON file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Data exported to JSON: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export JSON: {e}")
            return False
    
    def export_to_csv(self, data: List[Dict], filepath: str) -> bool:
        """Export data to CSV file"""
        try:
            if not data:
                return False
            
            fieldnames = ['name', 'category', 'price', 'description', 'country']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in data:
                    row = {
                        'name': product.get('name', ''),
                        'category': product.get('category', ''),
                        'price': product.get('price', ''),
                        'description': product.get('description', ''),
                        'country': product.get('country', '')
                    }
                    writer.writerow(row)
            
            self.logger.info(f"Data exported to CSV: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export CSV: {e}")
            return False
    
    def load_from_json(self, filepath: str) -> List[Dict]:
        """Load data from JSON file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"Data loaded from JSON: {filepath}")
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to load JSON: {e}")
            return []
