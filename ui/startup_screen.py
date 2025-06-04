"""
Startup Screen for POS System - Choose between Admin Interface and Kiosk Mode
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import subprocess
import sys
from ui.admin.login_screen import LoginScreen

class StartupScreen:
    def __init__(self, parent: tk.Tk):
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the startup screen UI"""
        # Clear parent window
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        self.parent.title("POS System V2 - Startup")
        self.parent.configure(bg='#f8f9fa')
        
        # Main container
        main_frame = tk.Frame(self.parent, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Title section
        title_frame = tk.Frame(main_frame, bg='#f8f9fa')
        title_frame.pack(fill=tk.X, pady=(0, 40))
        
        title_label = tk.Label(title_frame, text="POS System V2", 
                              font=("Arial", 32, "bold"), 
                              bg='#f8f9fa', fg='#2c3e50')
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, text="Point of Sale Management System", 
                                 font=("Arial", 14), 
                                 bg='#f8f9fa', fg='#7f8c8d')
        subtitle_label.pack(pady=(5, 0))
        
        # Options container
        options_frame = tk.Frame(main_frame, bg='#f8f9fa')
        options_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights for centering
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_rowconfigure(0, weight=1)
        
        # Admin Interface Section
        self.create_admin_section(options_frame)
        
        # Kiosk Section  
        self.create_kiosk_section(options_frame)
        
        # Footer
        footer_frame = tk.Frame(main_frame, bg='#f8f9fa')
        footer_frame.pack(fill=tk.X, pady=(40, 0))
        
        footer_label = tk.Label(footer_frame, text="© 2024 POS System V2", 
                               font=("Arial", 10), 
                               bg='#f8f9fa', fg='#95a5a6')
        footer_label.pack()
    
    def create_admin_section(self, parent):
        """Create the admin interface section"""
        admin_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        admin_frame.grid(row=0, column=0, padx=(0, 20), pady=20, sticky='nsew')
        
        # Configure internal padding
        admin_frame.grid_rowconfigure(0, weight=1)
        admin_frame.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(admin_frame, bg='white')
        content_frame.grid(row=0, column=0, padx=40, pady=40, sticky='nsew')
        
        # Icon (using text for now)
        icon_label = tk.Label(content_frame, text="🏪", font=("Arial", 48), bg='white')
        icon_label.pack(pady=(0, 20))
        
        # Title
        title_label = tk.Label(content_frame, text="Admin Interface", 
                              font=("Arial", 20, "bold"), bg='white', fg='#2c3e50')
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(content_frame, 
                             text="Access the full POS management system\nwith inventory, sales, and reporting features", 
                             font=("Arial", 12), bg='white', fg='#7f8c8d',
                             justify=tk.CENTER)
        desc_label.pack(pady=(0, 30))
        
        # Features list
        features_frame = tk.Frame(content_frame, bg='white')
        features_frame.pack(pady=(0, 30))
        
        features = [
            "• Inventory Management",
            "• Sales Reports",
            "• User Management", 
            "• Menu Configuration",
            "• Receipt Printing"
        ]
        
        for feature in features:
            feature_label = tk.Label(features_frame, text=feature, 
                                   font=("Arial", 10), bg='white', fg='#34495e')
            feature_label.pack(anchor='w')
        
        # Login button
        login_btn = tk.Button(content_frame, text="Login to Admin Panel", 
                             command=self.open_admin_login,
                             font=("Arial", 14, "bold"),
                             bg='#3498db', fg='white',
                             activebackground='#2980b9', activeforeground='white',
                             padx=30, pady=12, cursor='hand2',
                             relief=tk.FLAT)
        login_btn.pack()
    
    def create_kiosk_section(self, parent):
        """Create the kiosk launcher section"""
        kiosk_frame = tk.Frame(parent, bg='white', relief=tk.RAISED, bd=2)
        kiosk_frame.grid(row=0, column=1, padx=(20, 0), pady=20, sticky='nsew')
        
        # Configure internal padding
        kiosk_frame.grid_rowconfigure(0, weight=1)
        kiosk_frame.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(kiosk_frame, bg='white')
        content_frame.grid(row=0, column=0, padx=40, pady=40, sticky='nsew')
        
        # Icon
        icon_label = tk.Label(content_frame, text="📱", font=("Arial", 48), bg='white')
        icon_label.pack(pady=(0, 20))
        
        # Title
        title_label = tk.Label(content_frame, text="Self-Service Kiosk", 
                              font=("Arial", 20, "bold"), bg='white', fg='#2c3e50')
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(content_frame, 
                             text="Launch the customer-facing kiosk\nfor self-service ordering", 
                             font=("Arial", 12), bg='white', fg='#7f8c8d',
                             justify=tk.CENTER)
        desc_label.pack(pady=(0, 30))
        
        # Features list
        features_frame = tk.Frame(content_frame, bg='white')
        features_frame.pack(pady=(0, 30))
        
        features = [
            "• Touch-friendly Interface",
            "• Self-service Ordering",
            "• Payment Processing",
            "• Order Management",
            "• Customer Receipts"
        ]
        
        for feature in features:
            feature_label = tk.Label(features_frame, text=feature, 
                                   font=("Arial", 10), bg='white', fg='#34495e')
            feature_label.pack(anchor='w')
        
        # Status indicator
        self.kiosk_status_label = tk.Label(content_frame, text="Status: Ready to Launch", 
                                          font=("Arial", 10), bg='white', fg='#27ae60')
        self.kiosk_status_label.pack(pady=(0, 20))
        
        # Launch button
        launch_btn = tk.Button(content_frame, text="Launch Kiosk Application", 
                              command=self.launch_kiosk,
                              font=("Arial", 14, "bold"),
                              bg='#e74c3c', fg='white',
                              activebackground='#c0392b', activeforeground='white',
                              padx=30, pady=12, cursor='hand2',
                              relief=tk.FLAT)
        launch_btn.pack()
    
    def open_admin_login(self):
        """Open the admin login screen"""
        try:
            LoginScreen(self.parent)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open login screen: {str(e)}")
            print(f"Error opening login screen: {e}")
    
    def launch_kiosk(self):
        """Launch the kiosk electron application"""
        try:
            # Update status
            self.kiosk_status_label.config(text="Status: Launching...", fg='#f39c12')
            self.parent.update()
            
            # Path to the kiosk application
            kiosk_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kiosk_electron')
            
            # Check if kiosk directory exists
            if not os.path.exists(kiosk_path):
                messagebox.showerror("Error", 
                                   "Kiosk application not found.\n\n"
                                   "Please ensure the kiosk_electron directory exists and contains the kiosk application.")
                self.kiosk_status_label.config(text="Status: Error - Kiosk Not Found", fg='#e74c3c')
                return
            
            # Check if package.json exists
            package_json_path = os.path.join(kiosk_path, 'package.json')
            if not os.path.exists(package_json_path):
                messagebox.showerror("Error", 
                                   "Kiosk application package.json not found.\n\n"
                                   "Please ensure the kiosk application is properly set up.")
                self.kiosk_status_label.config(text="Status: Error - Invalid Setup", fg='#e74c3c')
                return
            
            # Try to launch the kiosk application
            if sys.platform.startswith('win'):
                # Windows
                subprocess.Popen(['npm', 'start'], cwd=kiosk_path, shell=True)
            else:
                # Unix/Linux/macOS
                subprocess.Popen(['npm', 'start'], cwd=kiosk_path)
            
            self.kiosk_status_label.config(text="Status: Launched Successfully", fg='#27ae60')
            messagebox.showinfo("Success", 
                              "Kiosk application launched successfully!\n\n"
                              "The kiosk interface should open in a new window.")
            
        except FileNotFoundError:
            messagebox.showerror("Error", 
                               "Node.js/npm not found.\n\n"
                               "Please install Node.js to run the kiosk application.")
            self.kiosk_status_label.config(text="Status: Error - Node.js Not Found", fg='#e74c3c')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch kiosk application: {str(e)}")
            self.kiosk_status_label.config(text="Status: Launch Failed", fg='#e74c3c')
            print(f"Error launching kiosk: {e}")
