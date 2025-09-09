"""
Progress tracking widget with logs display
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from utils.logger import LogCapture

class ProgressTracker(ttk.LabelFrame):
    """Widget for tracking progress and displaying logs"""
    
    def __init__(self, parent, log_capture):
        super().__init__(parent, text="Progress", padding="10")
        
        self.log_capture = log_capture
        self.progress_var = tk.StringVar(value="Ready to start scraping...")
        
        self._create_widgets()
        self._start_log_updates()
    
    def _create_widgets(self):
        """Create progress tracking widgets"""
        # Progress label
        ttk.Label(self, textvariable=self.progress_var).pack(anchor='w')
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            self,
            height=15,
            wrap='word',
            state='disabled'
        )
        self.log_text.pack(fill='both', expand=True, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs).pack(side='left')
    
    def _start_log_updates(self):
        """Start periodic log updates"""
        self._update_logs()
        self.after(1000, self._start_log_updates)  # Update every second
    
    def _update_logs(self):
        """Update log display"""
        try:
            logs = self.log_capture.get_recent(100)
            
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            
            for log_entry in logs:
                timestamp = log_entry['timestamp'].strftime("%H:%M:%S")
                level = log_entry['level']
                message = log_entry['message']
                formatted = f"[{timestamp}] [{level}] {message}\n"
                self.log_text.insert(tk.END, formatted)
            
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        except Exception:
            pass  # Ignore errors in log updates
    
    def update_progress(self, message, start_progress=False, stop_progress=False):
        """Update progress display"""
        self.progress_var.set(message)
        
        if start_progress:
            self.progress_bar.start()
        elif stop_progress:
            self.progress_bar.stop()
    
    def clear_logs(self):
        """Clear log display"""
        self.log_capture.clear()
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
