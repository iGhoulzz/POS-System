#!/usr/bin/env python3
"""
Simple test to verify basic POS system functionality
"""

import os
import sys
import sqlite3

def main():
    print("🚀 Testing POS System Components...")
    print("="*50)
    
    # Test 1: Database connection
    print("\n1. Testing Database Connection...")
    try:
        db_path = 'db/pos_system.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   ✅ Database connected - {user_count} users found")
            conn.close()
        else:
            print(f"   ❌ Database not found at {db_path}")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # Test 2: Import test
    print("\n2. Testing Module Imports...")
    modules = [
        'logic.user_manager',
        'ui.startup_screen',
        'ui.admin.admin_panel',
        'ui.admin.menu_manager'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except Exception as e:
            print(f"   ❌ {module} - {e}")
    
    # Test 3: User Manager
    print("\n3. Testing User Authentication...")
    try:
        from logic.user_manager import UserManager
        result = UserManager.authenticate_user('admin', 'admin123')
        if result:
            print("   ✅ Admin login works")
        else:
            print("   ❌ Admin login failed")
    except Exception as e:
        print(f"   ❌ Auth test error: {e}")
    
    # Test 4: Files exist
    print("\n4. Testing File Structure...")
    files_to_check = [
        'main.py',
        'ui/startup_screen.py',
        'ui/admin/admin_panel.py',
        'ui/admin/menu_manager.py',
        'db/pos_system.db'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} missing")
    
    print("\n" + "="*50)
    print("🎉 Basic tests completed!")
    print("\nTo run the system:")
    print("   python main.py")
    print("\nTo login to admin:")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == "__main__":
    main()
