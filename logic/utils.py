"""
Utility functions for the POS system
"""

import re
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import json

def hash_password(password: str) -> str:
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_number(value: str) -> bool:
    """Return True if the string represents a number"""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False

class POSUtils:
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency"""
        if amount is None:
            amount = 0.0
        return f"${float(amount):.2f}"
    
    @staticmethod
    def format_date(date_str: str, format_from: str = None, format_to: str = "%Y-%m-%d") -> str:
        """
        Format date string
        
        Args:
            date_str: Date string to format
            format_from: Current format (auto-detect if None)
            format_to: Target format
            
        Returns:
            Formatted date string
        """
        try:
            if format_from:
                date_obj = datetime.strptime(date_str, format_from)
            else:
                # Try common formats
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                    "%Y-%m-%d %H:%M:%S.%f"
                ]
                date_obj = None
                for fmt in formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if date_obj is None:
                    return date_str
            
            return date_obj.strftime(format_to)
        except Exception:
            return date_str
    
    @staticmethod
    def format_time(date_str: str) -> str:
        """Format datetime string to time only"""
        return POSUtils.format_date(date_str, format_to="%H:%M:%S")
    
    @staticmethod
    def get_current_date() -> str:
        """Get current date in YYYY-MM-DD format"""
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def get_current_datetime() -> str:
        """Get current datetime in YYYY-MM-DD HH:MM:SS format"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        # Check if it's 10 or 11 digits (with country code)
        return len(digits) in [10, 11]
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number"""
        digits = re.sub(r'\D', '', phone)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11:
            return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return phone
    
    @staticmethod
    def calculate_tax(amount: float, tax_rate: float) -> float:
        """Calculate tax amount"""
        return round(amount * tax_rate, 2)
    
    @staticmethod
    def calculate_total_with_tax(subtotal: float, tax_rate: float) -> tuple:
        """
        Calculate total with tax
        
        Args:
            subtotal: Subtotal amount
            tax_rate: Tax rate (e.g., 0.08 for 8%)
            
        Returns:
            Tuple of (tax_amount, total_amount)
        """
        tax_amount = POSUtils.calculate_tax(subtotal, tax_rate)
        total_amount = subtotal + tax_amount
        return tax_amount, total_amount
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a unique identifier"""
        return str(uuid.uuid4())
    
    @staticmethod
    def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
        """Truncate string to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """Safely convert value to float"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """Safely convert value to int"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_dict_get(dictionary: Dict, key: str, default: Any = None) -> Any:
        """Safely get value from dictionary"""
        return dictionary.get(key, default) if isinstance(dictionary, dict) else default
    
    @staticmethod
    def paginate_list(items: List, page: int, per_page: int = 10) -> Dict:
        """
        Paginate a list of items
        
        Args:
            items: List of items to paginate
            page: Page number (1-based)
            per_page: Items per page
            
        Returns:
            Dictionary with pagination info
        """
        total_items = len(items)
        total_pages = (total_items + per_page - 1) // per_page
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        return {
            'items': items[start_idx:end_idx],
            'page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    
    @staticmethod
    def search_list(items: List[Dict], search_term: str, search_fields: List[str]) -> List[Dict]:
        """
        Search through a list of dictionaries
        
        Args:
            items: List of dictionaries to search
            search_term: Term to search for
            search_fields: Fields to search in
            
        Returns:
            Filtered list of items
        """
        if not search_term:
            return items
        
        search_term = search_term.lower()
        filtered_items = []
        
        for item in items:
            for field in search_fields:
                field_value = str(item.get(field, '')).lower()
                if search_term in field_value:
                    filtered_items.append(item)
                    break
        
        return filtered_items
    
    @staticmethod
    def export_to_json(data: Any, file_path: str) -> bool:
        """
        Export data to JSON file
        
        Args:
            data: Data to export
            file_path: Path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def import_from_json(file_path: str) -> Any:
        """
        Import data from JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Imported data or None if failed
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error importing from JSON: {e}")
            return None
    
    @staticmethod
    def get_week_start_date(date_str: str = None) -> str:
        """
        Get the start date (Monday) of the week for a given date
        
        Args:
            date_str: Date string in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Week start date in YYYY-MM-DD format
        """
        if date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date_obj = datetime.now()
        
        # Calculate days to subtract to get to Monday (0 = Monday)
        days_to_subtract = date_obj.weekday()
        week_start = date_obj - timedelta(days=days_to_subtract)
        
        return week_start.strftime("%Y-%m-%d")
    
    @staticmethod
    def get_month_start_date(date_str: str = None) -> str:
        """
        Get the first day of the month for a given date
        
        Args:
            date_str: Date string in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Month start date in YYYY-MM-DD format
        """
        if date_str:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date_obj = datetime.now()
        
        month_start = date_obj.replace(day=1)
        return month_start.strftime("%Y-%m-%d")
