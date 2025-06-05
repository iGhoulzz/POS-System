"""
Login Screen for POS System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from logic.user_manager import UserManager
from config import DATABASE_PATH, DATABASE_NAME

class LoginScreen:
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login screen UI"""
        # Clear parent window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.parent.title("POS System - Login")
        
        # Center the login form
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(expand=True)
        
        # Login form frame
        login_frame = ttk.LabelFrame(main_frame, text="Login", padding=20)
        login_frame.pack(padx=50, pady=50)
        
        # Title
        title_label = ttk.Label(login_frame, text="POS System V2", 
                               font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Username field
        ttk.Label(login_frame, text="Username:", font=("Arial", 12)).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(login_frame, textvariable=self.username_var, 
                                       font=("Arial", 12), width=20)
        self.username_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Password field
        ttk.Label(login_frame, text="Password:", font=("Arial", 12)).grid(
            row=2, column=0, sticky=tk.W, pady=5)
        
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(login_frame, textvariable=self.password_var, 
                                       show="*", font=("Arial", 12), width=20)
        self.password_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Login button
        login_btn = ttk.Button(login_frame, text="Login", command=self.login,
                              width=15)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        # Bind Enter key to login
        self.parent.bind('<Return>', lambda event: self.login())
        
        # Set initial focus
        self.username_entry.focus()
        
        # Default credentials info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=10)
        
        info_label = ttk.Label(info_frame, text="Default login: admin / admin123", 
                              font=("Arial", 10), foreground="gray")
        info_label.pack()
    
    def login(self):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
          # Authenticate user
        user = UserManager.authenticate_user(username, password)
        
        if user:
            # Login successful, open appropriate interface
            self.open_main_interface(user)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_var.set("")
            self.password_entry.focus()
    
    def open_main_interface(self, user):
        """Open the main interface based on user role"""
        try:
            # Construct database path
            db_path = os.path.join(DATABASE_PATH, DATABASE_NAME)

            from ui.admin.admin_panel import AdminPanel
            from ui.admin.pos_screen import POSWindow
            from ui.admin.kitchen_display import KitchenDisplayWindow

            role = user.get("role")

            if role == "admin":
                AdminPanel(self.parent, db_path)
            elif role == "cashier":
                POSWindow(self.parent, user)
            elif role == "kitchen":
                KitchenDisplayWindow(self.parent)
            else:
                messagebox.showerror("Error", f"Unknown role: {role}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open main interface: {str(e)}")
            print(f"Error opening main interface: {e}")
