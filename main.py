#!/usr/bin/env python3
"""
POS System V2 - Main Entry Point
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from db.init_db import initialize_database
from ui.startup_screen import StartupScreen

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('pos_system.log')  # File output
    ]
)

def main():
    """Main application entry point"""
    try:
        print("🚀 Starting POS System V2...")
        logging.info("POS System V2 startup initiated")
        
        # Initialize database
        print("📊 Initializing database...")
        logging.info("Initializing database")
        initialize_database()
        print("✅ Database initialized successfully")
        logging.info("Database initialization completed")
        
        # Create main window
        print("🖥️ Creating main application window...")
        logging.info("Creating main application window")
        root = tk.Tk()
        root.title(APP_NAME)
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        root.resizable(True, True)
        
        # Start with startup screen
        print("🎯 Loading startup screen...")
        logging.info("Loading startup screen")
        startup_screen = StartupScreen(root)
        print("✅ POS System ready!")
        logging.info("POS System startup completed successfully")
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        error_msg = f"Failed to start application: {str(e)}"
        print(f"❌ {error_msg}")
        logging.error(error_msg)
        messagebox.showerror("Error", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
