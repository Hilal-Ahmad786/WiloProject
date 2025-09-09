"""
Browser settings widget
"""

import tkinter as tk
from tkinter import ttk

class BrowserSettings(ttk.LabelFrame):
    """Widget for browser configuration"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Browser Settings", padding="10")
        self.settings = settings
        self._create_widgets()
    
    def _create_widgets(self):
        """Create browser settings widgets"""
        # Headless mode
        self.headless_var = tk.BooleanVar(value=self.settings.headless_mode)
        ttk.Checkbutton(
            self,
            text="Run in headless mode (no browser window)",
            variable=self.headless_var
        ).pack(anchor='w')
        
        # Delay settings
        delay_frame = ttk.Frame(self)
        delay_frame.pack(fill='x', pady=5)
        
        ttk.Label(delay_frame, text="Page load delay (seconds):").pack(side='left')
        self.delay_var = tk.StringVar(value=str(self.settings.page_load_delay))
        delay_spinbox = ttk.Spinbox(
            delay_frame,
            from_=1,
            to=10,
            textvariable=self.delay_var,
            width=5
        )
        delay_spinbox.pack(side='left', padx=5)
        
        # Timeout settings
        timeout_frame = ttk.Frame(self)
        timeout_frame.pack(fill='x', pady=5)
        
        ttk.Label(timeout_frame, text="Browser timeout (seconds):").pack(side='left')
        self.timeout_var = tk.StringVar(value=str(self.settings.browser_timeout))
        timeout_spinbox = ttk.Spinbox(
            timeout_frame,
            from_=10,
            to=120,
            textvariable=self.timeout_var,
            width=5
        )
        timeout_spinbox.pack(side='left', padx=5)
    
    def get_settings(self):
        """Get current browser settings"""
        return {
            'headless_mode': self.headless_var.get(),
            'page_load_delay': int(self.delay_var.get()),
            'browser_timeout': int(self.timeout_var.get())
        }
