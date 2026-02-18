"""
Cashier Panel - Restricted interface for cashier role users.
Only provides access to POS order processing functionality.
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from .pos_screen import POSTab


class CashierPanel:
    def __init__(self, master, db_path, user):
        self.master = master
        self.db_path = db_path
        self.user = user
        self.setup_ui()

    def setup_ui(self):
        """Setup the cashier panel UI"""
        # Clear all existing widgets from master window
        for widget in self.master.winfo_children():
            widget.destroy()

        # Configure main window
        self.master.configure(bg='#f8f9fa')
        self.master.title("POS System - Cashier")

        # Main container
        self.main_frame = tk.Frame(self.master, bg='#f8f9fa')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create header
        self.create_header()

        # Create POS content area
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        POSTab(content_frame, self.user)

    def create_header(self):
        """Create the header with title and user info"""
        header_frame = tk.Frame(self.main_frame, bg='#27ae60', height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Title
        title_label = tk.Label(header_frame, text="🛒 POS - Cashier",
                               font=('Segoe UI', 16, 'bold'),
                               fg='white', bg='#27ae60')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)

        # User info and logout
        user_frame = tk.Frame(header_frame, bg='#27ae60')
        user_frame.pack(side=tk.RIGHT, padx=20, pady=15)

        user_display = self.user.get('full_name', 'Cashier')
        user_label = tk.Label(user_frame, text=f"👤 {user_display} (Cashier)",
                              font=('Segoe UI', 11),
                              fg='white', bg='#27ae60')
        user_label.pack(side=tk.LEFT, padx=(0, 15))

        logout_btn = tk.Button(user_frame, text="🚪 Logout",
                               command=self.logout,
                               font=('Segoe UI', 10),
                               bg='#e74c3c', fg='white',
                               relief=tk.FLAT, padx=15, pady=5,
                               cursor='hand2')
        logout_btn.pack(side=tk.RIGHT)

    def logout(self):
        """Return to startup screen"""
        from ui.startup_screen import StartupScreen
        StartupScreen(self.master)
