# Configuration file for POS system

# Database configuration
DATABASE_NAME = "pos_system.db"
DATABASE_PATH = "db/"

# Application settings
APP_NAME = "POS System V2"
APP_VERSION = "2.0.0"
DEBUG_MODE = False

# UI settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
THEME = "modern"

# Receipt settings
RECEIPT_PRINTER_NAME = ""
RECEIPT_WIDTH = 80  # characters
COMPANY_NAME = "Your Business Name"
COMPANY_ADDRESS = "123 Business St, City, State 12345"
COMPANY_PHONE = "(555) 123-4567"

# Tax settings
TAX_RATE = 0.08  # 8% tax rate

# Kiosk settings
KIOSK_PORT = 3000
KIOSK_TIMEOUT = 60  # seconds of inactivity before reset
