"""
Country selection widget
"""

import tkinter as tk
from tkinter import ttk
from config.countries import COUNTRIES, get_all_countries

class CountrySelector(ttk.LabelFrame):
    """Widget for selecting target country"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Country Selection", padding="10")
        self.settings = settings
        self.selected_country = tk.StringVar()
        self._create_widgets()
    
    def _create_widgets(self):
        """Create country selection widgets"""
        ttk.Label(self, text="Select Target Country:").pack(anchor='w')
        
        # Country dropdown
        countries = [COUNTRIES[key]['name'] for key in get_all_countries()]
        self.country_combo = ttk.Combobox(
            self,
            textvariable=self.selected_country,
            values=countries,
            state="readonly",
            width=30
        )
        self.country_combo.pack(anchor='w', pady=5)
        self.country_combo.set("Deutschland")  # Default to Germany
        
        # Info display
        self.info_text = tk.Text(self, height=3, state='disabled', wrap='word')
        self.info_text.pack(fill='x', pady=5)
        
        # Bind selection change
        self.country_combo.bind('<<ComboboxSelected>>', self._on_country_changed)
        self._on_country_changed()  # Initialize
    
    def _on_country_changed(self, event=None):
        """Handle country selection change"""
        try:
            country_name = self.selected_country.get()
            # Find country data
            country_data = None
            for key, data in COUNTRIES.items():
                if data['name'] == country_name:
                    country_data = data
                    break
            
            if country_data:
                info = f"Language: {country_data['language']}\n"
                info += f"Pump Selection Text: {country_data['hydraulic_pump_text']}"
                
                self.info_text.config(state='normal')
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(1.0, info)
                self.info_text.config(state='disabled')
        except Exception:
            pass
    
    def get_selected_country_key(self):
        """Get the key for selected country"""
        country_name = self.selected_country.get()
        for key, data in COUNTRIES.items():
            if data['name'] == country_name:
                return key
        return 'germany'  # Default
