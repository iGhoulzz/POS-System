"""
Report generation functionality
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import csv
import os
from db.db_utils import execute_query_dict

class ReportGenerator:
    @staticmethod
    def get_daily_sales_report(date: str) -> Dict:
        """
        Generate daily sales report
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with sales data
        """
        try:
            # Total sales for the day
            sales_query = '''
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales,
                    SUM(tax_amount) as total_tax,
                    AVG(total_amount) as average_order
                FROM orders
                WHERE DATE(created_at) = ? AND status != 'cancelled'
            '''
            sales_data = execute_query_dict(sales_query, (date,), 'one')
            
            # Sales by payment method
            payment_query = '''
                SELECT 
                    payment_method,
                    COUNT(*) as count,
                    SUM(total_amount) as total
                FROM orders
                WHERE DATE(created_at) = ? AND status != 'cancelled'
                GROUP BY payment_method
            '''
            payment_data = execute_query_dict(payment_query, (date,), 'all') or []
            
            # Top selling items
            items_query = '''
                SELECT 
                    mi.name,
                    SUM(oi.quantity) as total_quantity,
                    SUM(oi.total_price) as total_revenue
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                JOIN orders o ON oi.order_id = o.id
                WHERE DATE(o.created_at) = ? AND o.status != 'cancelled'
                GROUP BY mi.id, mi.name
                ORDER BY total_quantity DESC
                LIMIT 10
            '''
            top_items = execute_query_dict(items_query, (date,), 'all') or []
            
            # Hourly sales breakdown
            hourly_query = '''
                SELECT 
                    strftime('%H', created_at) as hour,
                    COUNT(*) as orders,
                    SUM(total_amount) as sales
                FROM orders
                WHERE DATE(created_at) = ? AND status != 'cancelled'
                GROUP BY strftime('%H', created_at)
                ORDER BY hour
            '''
            hourly_data = execute_query_dict(hourly_query, (date,), 'all') or []
            
            return {
                'date': date,
                'sales_summary': sales_data or {
                    'total_orders': 0,
                    'total_sales': 0.0,
                    'total_tax': 0.0,
                    'average_order': 0.0
                },
                'payment_methods': payment_data,
                'top_items': top_items,
                'hourly_breakdown': hourly_data
            }
            
        except Exception as e:
            print(f"Error generating daily sales report: {e}")
            return {}
    
    @staticmethod
    def get_weekly_sales_report(start_date: str) -> Dict:
        """
        Generate weekly sales report
        
        Args:
            start_date: Start date of the week (Monday) in YYYY-MM-DD format
            
        Returns:
            Dictionary with weekly sales data
        """
        try:
            # Calculate end date (Sunday)
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = (start + timedelta(days=6)).strftime('%Y-%m-%d')
            
            # Daily breakdown for the week
            daily_query = '''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as orders,
                    SUM(total_amount) as sales
                FROM orders
                WHERE DATE(created_at) BETWEEN ? AND ? AND status != 'cancelled'
                GROUP BY DATE(created_at)
                ORDER BY date
            '''
            daily_data = execute_query_dict(daily_query, (start_date, end_date), 'all') or []
            
            # Week totals
            totals_query = '''
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales,
                    SUM(tax_amount) as total_tax,
                    AVG(total_amount) as average_order
                FROM orders
                WHERE DATE(created_at) BETWEEN ? AND ? AND status != 'cancelled'
            '''
            totals = execute_query_dict(totals_query, (start_date, end_date), 'one')
            
            return {
                'week_start': start_date,
                'week_end': end_date,
                'daily_breakdown': daily_data,
                'week_totals': totals or {
                    'total_orders': 0,
                    'total_sales': 0.0,
                    'total_tax': 0.0,
                    'average_order': 0.0
                }
            }
            
        except Exception as e:
            print(f"Error generating weekly sales report: {e}")
            return {}
    
    @staticmethod
    def get_monthly_sales_report(year: int, month: int) -> Dict:
        """
        Generate monthly sales report
        
        Args:
            year: Year
            month: Month (1-12)
            
        Returns:
            Dictionary with monthly sales data
        """
        try:
            # Format month for SQL query
            month_str = f"{year}-{month:02d}"
            
            # Monthly totals
            totals_query = '''
                SELECT 
                    COUNT(*) as total_orders,
                    SUM(total_amount) as total_sales,
                    SUM(tax_amount) as total_tax,
                    AVG(total_amount) as average_order
                FROM orders
                WHERE strftime('%Y-%m', created_at) = ? AND status != 'cancelled'
            '''
            totals = execute_query_dict(totals_query, (month_str,), 'one')
            
            # Daily breakdown
            daily_query = '''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as orders,
                    SUM(total_amount) as sales
                FROM orders
                WHERE strftime('%Y-%m', created_at) = ? AND status != 'cancelled'
                GROUP BY DATE(created_at)
                ORDER BY date
            '''
            daily_data = execute_query_dict(daily_query, (month_str,), 'all') or []
            
            # Category performance
            category_query = '''
                SELECT 
                    c.name as category,
                    SUM(oi.quantity) as total_quantity,
                    SUM(oi.total_price) as total_revenue
                FROM order_items oi
                JOIN menu_items mi ON oi.menu_item_id = mi.id
                JOIN categories c ON mi.category_id = c.id
                JOIN orders o ON oi.order_id = o.id
                WHERE strftime('%Y-%m', o.created_at) = ? AND o.status != 'cancelled'
                GROUP BY c.id, c.name
                ORDER BY total_revenue DESC
            '''
            category_data = execute_query_dict(category_query, (month_str,), 'all') or []
            
            return {
                'year': year,
                'month': month,
                'month_totals': totals or {
                    'total_orders': 0,
                    'total_sales': 0.0,
                    'total_tax': 0.0,
                    'average_order': 0.0
                },
                'daily_breakdown': daily_data,
                'category_performance': category_data
            }
            
        except Exception as e:
            print(f"Error generating monthly sales report: {e}")
            return {}
    
    @staticmethod
    def export_sales_report_csv(report_data: Dict, output_path: str) -> bool:
        """
        Export sales report data to CSV
        
        Args:
            report_data: Report data dictionary
            output_path: Path to save CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header based on report type
                if 'daily_breakdown' in report_data:
                    if 'week_start' in report_data:
                        # Weekly report
                        writer.writerow(['Weekly Sales Report'])
                        writer.writerow(['Week:', f"{report_data['week_start']} to {report_data['week_end']}"])
                        writer.writerow([])
                        writer.writerow(['Date', 'Orders', 'Sales'])
                        for day in report_data['daily_breakdown']:
                            writer.writerow([day['date'], day['orders'], f"${day['sales']:.2f}"])
                    else:
                        # Monthly report
                        writer.writerow(['Monthly Sales Report'])
                        writer.writerow(['Month:', f"{report_data['year']}-{report_data['month']:02d}"])
                        writer.writerow([])
                        writer.writerow(['Date', 'Orders', 'Sales'])
                        for day in report_data['daily_breakdown']:
                            writer.writerow([day['date'], day['orders'], f"${day['sales']:.2f}"])
                else:
                    # Daily report
                    writer.writerow(['Daily Sales Report'])
                    writer.writerow(['Date:', report_data['date']])
                    writer.writerow([])
                    
                    # Sales summary
                    summary = report_data['sales_summary']
                    writer.writerow(['Summary'])
                    writer.writerow(['Total Orders:', summary['total_orders']])
                    writer.writerow(['Total Sales:', f"${summary['total_sales']:.2f}"])
                    writer.writerow(['Total Tax:', f"${summary['total_tax']:.2f}"])
                    writer.writerow(['Average Order:', f"${summary['average_order']:.2f}"])
                    writer.writerow([])
                    
                    # Top items
                    if report_data['top_items']:
                        writer.writerow(['Top Selling Items'])
                        writer.writerow(['Item', 'Quantity Sold', 'Revenue'])
                        for item in report_data['top_items']:
                            writer.writerow([item['name'], item['total_quantity'], f"${item['total_revenue']:.2f}"])
            
            return True
            
        except Exception as e:
            print(f"Error exporting CSV report: {e}")
            return False
    
    @staticmethod
    def get_expense_report(start_date: str, end_date: str) -> Dict:
        """
        Generate expense report
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dictionary with expense data
        """
        try:
            # Total expenses
            total_query = '''
                SELECT 
                    COUNT(*) as total_count,
                    SUM(amount) as total_amount
                FROM expenses
                WHERE date BETWEEN ? AND ?
            '''
            totals = execute_query_dict(total_query, (start_date, end_date), 'one')
            
            # Expenses by category
            category_query = '''
                SELECT 
                    category,
                    COUNT(*) as count,
                    SUM(amount) as total
                FROM expenses
                WHERE date BETWEEN ? AND ?
                GROUP BY category
                ORDER BY total DESC
            '''
            by_category = execute_query_dict(category_query, (start_date, end_date), 'all') or []
            
            # Daily breakdown
            daily_query = '''
                SELECT 
                    date,
                    COUNT(*) as count,
                    SUM(amount) as total
                FROM expenses
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date
            '''
            daily_data = execute_query_dict(daily_query, (start_date, end_date), 'all') or []
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'totals': totals or {'total_count': 0, 'total_amount': 0.0},
                'by_category': by_category,
                'daily_breakdown': daily_data
            }
            
        except Exception as e:
            print(f"Error generating expense report: {e}")
            return {}
