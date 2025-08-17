"""
Add sample data to the database if it's empty
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_utils import execute_query_dict
import sqlite3

def add_sample_data():
    """Add sample data if the database is empty"""
    try:
        # Check if we have any menu items
        items_count = execute_query_dict("SELECT COUNT(*) as count FROM menu_items", fetch='one')
        
        if items_count and items_count['count'] == 0:
            print("Adding sample data to database...")
            
            # Add sample categories
            categories = [
                ('Appetizers', 'Starter dishes and small plates'),
                ('Main Courses', 'Primary dishes and entrees'),
                ('Beverages', 'Drinks and refreshments'),
                ('Desserts', 'Sweet treats and desserts')
            ]
            
            category_ids = {}
            for name, description in categories:
                try:
                    execute_query_dict(
                        "INSERT INTO categories (name, description) VALUES (?, ?)",
                        (name, description)
                    )
                    # Get the category ID
                    result = execute_query_dict(
                        "SELECT id FROM categories WHERE name = ?",
                        (name,), 'one'
                    )
                    if result:
                        category_ids[name] = result['id']
                except Exception as e:
                    print(f"Warning: Could not add category {name}: {e}")
            
            # Add sample menu items
            if category_ids:
                menu_items = [
                    ('Buffalo Wings', 'Spicy chicken wings with ranch dip', 8.99, category_ids.get('Appetizers', 1)),
                    ('Caesar Salad', 'Fresh romaine with caesar dressing', 7.99, category_ids.get('Appetizers', 1)),
                    ('Grilled Chicken', 'Herb-seasoned grilled chicken breast', 14.99, category_ids.get('Main Courses', 2)),
                    ('Beef Burger', 'Classic beef burger with fries', 12.99, category_ids.get('Main Courses', 2)),
                    ('Soda', 'Refreshing soft drink', 2.99, category_ids.get('Beverages', 3)),
                    ('Coffee', 'Freshly brewed coffee', 2.49, category_ids.get('Beverages', 3)),
                    ('Chocolate Cake', 'Rich chocolate layer cake', 5.99, category_ids.get('Desserts', 4)),
                    ('Ice Cream', 'Vanilla ice cream scoop', 3.99, category_ids.get('Desserts', 4))
                ]
                
                for name, description, price, category_id in menu_items:
                    try:
                        execute_query_dict(
                            "INSERT INTO menu_items (name, description, price, category_id) VALUES (?, ?, ?, ?)",
                            (name, description, price, category_id)
                        )
                    except Exception as e:
                        print(f"Warning: Could not add menu item {name}: {e}")
                
                print("✅ Sample data added successfully!")
                return True
        else:
            print("Database already contains menu items.")
            return True
            
    except Exception as e:
        print(f"❌ Error adding sample data: {e}")
        return False

if __name__ == "__main__":
    add_sample_data()