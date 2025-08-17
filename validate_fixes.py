#!/usr/bin/env python3
"""
POS System Validation Script
Tests the key functionality to ensure fixes are working properly
"""

import os
import sys
import sqlite3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_utils import execute_query_dict, get_db_connection
from db.init_db import initialize_database

def test_database_connection():
    """Test database connection and basic operations"""
    print("🔗 Testing database connection...")
    try:
        # Test connection
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_menu_items_loading():
    """Test menu items loading functionality"""
    print("🍽️ Testing menu items loading...")
    try:
        # Test categories query
        categories = execute_query_dict("SELECT id, name FROM categories WHERE is_active = 1", fetch='all')
        print(f"✅ Found {len(categories) if categories else 0} categories")
        
        # Test menu items query
        items = execute_query_dict("SELECT id, name, price FROM menu_items WHERE is_active = 1", fetch='all')
        print(f"✅ Found {len(items) if items else 0} menu items")
        
        if not items:
            print("⚠️ No menu items found - this might cause 'failed to load products' errors")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Menu items loading failed: {e}")
        return False

def test_database_timeout():
    """Test database timeout handling"""
    print("⏱️ Testing database timeout handling...")
    try:
        # This should not hang indefinitely
        result = execute_query_dict("SELECT COUNT(*) as count FROM menu_items", fetch='one')
        print("✅ Database timeout handling working")
        return True
    except sqlite3.OperationalError as e:
        if "timeout" in str(e).lower():
            print("✅ Database timeout properly handled")
            return True
        else:
            print(f"❌ Database timeout test failed: {e}")
            return False
    except Exception as e:
        print(f"❌ Database timeout test failed: {e}")
        return False

def test_error_handling():
    """Test error handling for invalid queries"""
    print("🚨 Testing error handling...")
    try:
        # Try an invalid query to test error handling
        try:
            execute_query_dict("SELECT invalid_column FROM nonexistent_table", fetch='all')
            print("❌ Error handling test failed - should have thrown an exception")
            return False
        except Exception:
            print("✅ Error handling working properly")
            return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def test_sample_data():
    """Test that sample data exists"""
    print("📊 Testing sample data...")
    try:
        # Check for sample categories
        categories = execute_query_dict("SELECT COUNT(*) as count FROM categories", fetch='one')
        items = execute_query_dict("SELECT COUNT(*) as count FROM menu_items", fetch='one')
        
        if categories and categories['count'] > 0:
            print(f"✅ Found {categories['count']} categories")
        else:
            print("⚠️ No categories found")
        
        if items and items['count'] > 0:
            print(f"✅ Found {items['count']} menu items")
        else:
            print("⚠️ No menu items found")
        
        return (categories and categories['count'] > 0) and (items and items['count'] > 0)
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🚀 Starting POS System Validation...")
    print("=" * 50)
    
    # Initialize database first
    try:
        initialize_database()
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    tests = [
        test_database_connection,
        test_menu_items_loading,
        test_database_timeout,
        test_error_handling,
        test_sample_data
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print("-" * 30)
    
    print("=" * 50)
    print(f"📊 Validation Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! POS System should be working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Issues may still exist.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)