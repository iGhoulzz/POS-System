"""
Database initialization and schema creation
"""

import sqlite3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_NAME, DATABASE_PATH

def initialize_database():
    """Initialize the database with required tables"""
    db_file = os.path.join(DATABASE_PATH, DATABASE_NAME)
    
    # Create database directory if it doesn't exist
    os.makedirs(DATABASE_PATH, exist_ok=True)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Users table with optional email and last_login fields
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('admin', 'cashier', 'kitchen')),
            full_name TEXT NOT NULL,
            email TEXT,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')

    # Add missing columns if database already exists without them
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    if 'email' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if 'last_login' not in existing_cols:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
      # Menu items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            cost_price REAL DEFAULT 0.0,
            price REAL NOT NULL,
            category_id INTEGER,
            image_path TEXT,
            is_active BOOLEAN DEFAULT 1,
            preparation_time INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT UNIQUE NOT NULL,
            customer_name TEXT,
            order_type TEXT CHECK (order_type IN ('dine_in', 'takeout', 'delivery')),
            total_amount REAL NOT NULL,
            tax_amount REAL NOT NULL,
            payment_method TEXT,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'preparing', 'ready', 'completed', 'cancelled')),
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            special_instructions TEXT,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
        )
    ''')
    
    # Expenses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date DATE NOT NULL,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    # Create default admin user if no users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        import hashlib
        password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
        ''', ('admin', password_hash, 'admin', 'System Administrator'))
    
    # Insert default settings
    default_settings = [
        ('tax_rate', '0.08', 'Sales tax rate'),
        ('receipt_header', 'Your Business Name', 'Receipt header text'),
        ('receipt_footer', 'Thank you for your business!', 'Receipt footer text'),
    ]
    
    for key, value, description in default_settings:
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value, description)
            VALUES (?, ?, ?)
        ''', (key, value, description))
    
    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {db_file}")

if __name__ == "__main__":
    initialize_database()
