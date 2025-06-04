"""
Order management logic
"""

import time
from datetime import datetime
from typing import List, Dict, Optional
from db.db_utils import execute_query_dict, execute_query

class OrderManager:
    @staticmethod
    def generate_order_number() -> str:
        """Generate a unique order number"""
        timestamp = int(time.time())
        return f"ORD{timestamp}"
    
    @staticmethod
    def create_order(customer_name: str, order_type: str, items: List[Dict], 
                    payment_method: str, created_by: int, tax_rate: float = 0.08) -> Optional[int]:
        """
        Create a new order
        
        Args:
            customer_name: Customer name
            order_type: Type of order ('dine_in', 'takeout', 'delivery')
            items: List of order items with menu_item_id, quantity, unit_price
            payment_method: Payment method
            created_by: User ID who created the order
            tax_rate: Tax rate to apply
        
        Returns:
            Order ID if successful, None otherwise
        """
        try:
            # Calculate totals
            subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            # Create order
            order_number = OrderManager.generate_order_number()
            order_query = '''
                INSERT INTO orders (order_number, customer_name, order_type, 
                                  total_amount, tax_amount, payment_method, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            execute_query(order_query, (order_number, customer_name, order_type,
                                      total_amount, tax_amount, payment_method, created_by))
            
            # Get the order ID
            order_id_query = "SELECT id FROM orders WHERE order_number = ?"
            order_result = execute_query_dict(order_id_query, (order_number,), 'one')
            order_id = order_result['id']
            
            # Add order items
            for item in items:
                item_total = item['quantity'] * item['unit_price']
                item_query = '''
                    INSERT INTO order_items (order_id, menu_item_id, quantity, 
                                           unit_price, total_price, special_instructions)
                    VALUES (?, ?, ?, ?, ?, ?)
                '''
                execute_query(item_query, (order_id, item['menu_item_id'], item['quantity'],
                                         item['unit_price'], item_total, 
                                         item.get('special_instructions', '')))
            
            return order_id
        
        except Exception as e:
            print(f"Error creating order: {e}")
            return None
    
    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Dict]:
        """Get order details by ID"""
        query = '''
            SELECT o.*, u.full_name as created_by_name
            FROM orders o
            LEFT JOIN users u ON o.created_by = u.id
            WHERE o.id = ?
        '''
        return execute_query_dict(query, (order_id,), 'one')
    
    @staticmethod
    def get_order_items(order_id: int) -> List[Dict]:
        """Get items for an order"""
        query = '''
            SELECT oi.*, mi.name as item_name, mi.description
            FROM order_items oi
            JOIN menu_items mi ON oi.menu_item_id = mi.id
            WHERE oi.order_id = ?
        '''
        return execute_query_dict(query, (order_id,), 'all') or []
    
    @staticmethod
    def get_pending_orders() -> List[Dict]:
        """Get all pending orders for kitchen display"""
        query = '''
            SELECT o.*, u.full_name as created_by_name
            FROM orders o
            LEFT JOIN users u ON o.created_by = u.id
            WHERE o.status IN ('pending', 'preparing')
            ORDER BY o.created_at
        '''
        return execute_query_dict(query, fetch='all') or []
    
    @staticmethod
    def get_orders_by_date(date: str) -> List[Dict]:
        """Get orders for a specific date"""
        query = '''
            SELECT o.*, u.full_name as created_by_name
            FROM orders o
            LEFT JOIN users u ON o.created_by = u.id
            WHERE DATE(o.created_at) = ?
            ORDER BY o.created_at DESC
        '''
        return execute_query_dict(query, (date,), 'all') or []
    
    @staticmethod
    def update_order_status(order_id: int, status: str) -> bool:
        """
        Update order status
        
        Args:
            order_id: Order ID
            status: New status ('pending', 'preparing', 'ready', 'completed', 'cancelled')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "UPDATE orders SET status = ? WHERE id = ?"
            if status == 'completed':
                query = "UPDATE orders SET status = ?, completed_at = CURRENT_TIMESTAMP WHERE id = ?"
                execute_query(query, (status, order_id))
            else:
                execute_query(query, (status, order_id))
            return True
        except Exception as e:
            print(f"Error updating order status: {e}")
            return False
    
    @staticmethod
    def get_sales_summary(start_date: str, end_date: str) -> Dict:
        """
        Get sales summary for a date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            Dictionary with sales summary
        """
        try:
            query = '''
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales,
                    SUM(tax_amount) as total_tax,
                    AVG(total_amount) as average_order
                FROM orders
                WHERE DATE(created_at) BETWEEN ? AND ?
                AND status != 'cancelled'
            '''
            result = execute_query_dict(query, (start_date, end_date), 'one')
            return result or {
                'total_orders': 0,
                'total_sales': 0.0,
                'total_tax': 0.0,
                'average_order': 0.0
            }
        except Exception as e:
            print(f"Error getting sales summary: {e}")
            return {
                'total_orders': 0,
                'total_sales': 0.0,
                'total_tax': 0.0,
                'average_order': 0.0
            }
