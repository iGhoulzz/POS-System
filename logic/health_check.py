"""
Health check utilities for POS system
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_utils import execute_query_dict, get_db_connection

class HealthChecker:
    """System health checker for POS components"""
    
    @staticmethod
    def check_database_connection():
        """Check if database connection is working"""
        try:
            conn = get_db_connection()
            conn.execute("SELECT 1")
            conn.close()
            return True, "Database connection OK"
        except Exception as e:
            return False, f"Database connection failed: {str(e)}"
    
    @staticmethod
    def check_menu_data():
        """Check if menu data is available"""
        try:
            categories = execute_query_dict("SELECT COUNT(*) as count FROM categories WHERE is_active = 1", fetch='one')
            items = execute_query_dict("SELECT COUNT(*) as count FROM menu_items WHERE is_active = 1", fetch='one')
            
            cat_count = categories['count'] if categories else 0
            item_count = items['count'] if items else 0
            
            if cat_count == 0:
                return False, "No categories found - products may not load"
            elif item_count == 0:
                return False, "No menu items found - products will not load"
            else:
                return True, f"Menu data OK: {cat_count} categories, {item_count} items"
        except Exception as e:
            return False, f"Menu data check failed: {str(e)}"
    
    @staticmethod
    def check_database_performance():
        """Check database performance"""
        try:
            import time
            start_time = time.time()
            execute_query_dict("SELECT COUNT(*) FROM menu_items", fetch='one')
            end_time = time.time()
            
            query_time = end_time - start_time
            if query_time > 5.0:
                return False, f"Database queries are slow ({query_time:.2f}s)"
            else:
                return True, f"Database performance OK ({query_time:.3f}s)"
        except Exception as e:
            return False, f"Performance check failed: {str(e)}"
    
    @staticmethod
    def run_full_health_check():
        """Run all health checks and return results"""
        checks = [
            ("Database Connection", HealthChecker.check_database_connection),
            ("Menu Data", HealthChecker.check_menu_data),
            ("Database Performance", HealthChecker.check_database_performance)
        ]
        
        results = []
        all_passed = True
        
        for name, check_func in checks:
            try:
                passed, message = check_func()
                results.append((name, passed, message))
                if not passed:
                    all_passed = False
            except Exception as e:
                results.append((name, False, f"Check failed: {str(e)}"))
                all_passed = False
        
        return all_passed, results
    
    @staticmethod
    def get_health_summary():
        """Get a simple health summary"""
        all_passed, results = HealthChecker.run_full_health_check()
        
        if all_passed:
            return "✅ System is healthy"
        else:
            failed_checks = [name for name, passed, _ in results if not passed]
            return f"⚠️ Issues found: {', '.join(failed_checks)}"

if __name__ == "__main__":
    all_passed, results = HealthChecker.run_full_health_check()
    
    print("🏥 POS System Health Check")
    print("=" * 40)
    
    for name, passed, message in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}: {message}")
    
    print("=" * 40)
    if all_passed:
        print("🎉 All checks passed! System is healthy.")
    else:
        print("⚠️ Some issues found. Check the details above.")