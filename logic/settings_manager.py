"""
Settings management functionality
"""

from typing import Dict, List, Optional, Any
from db.db_utils import execute_query_dict, execute_query

class SettingsManager:
    @staticmethod
    def get_setting(key: str) -> Optional[str]:
        """
        Get a setting value by key
        
        Args:
            key: Setting key
            
        Returns:
            Setting value or None if not found
        """
        query = "SELECT value FROM settings WHERE key = ?"
        result = execute_query_dict(query, (key,), 'one')
        return result['value'] if result else None
    
    @staticmethod
    def set_setting(key: str, value: str, description: str = None) -> bool:
        """
        Set a setting value
        
        Args:
            key: Setting key
            value: Setting value
            description: Setting description (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if setting exists
            existing = SettingsManager.get_setting(key)
            
            if existing is not None:
                # Update existing setting
                query = "UPDATE settings SET value = ? WHERE key = ?"
                execute_query(query, (value, key))
            else:
                # Insert new setting
                query = "INSERT INTO settings (key, value, description) VALUES (?, ?, ?)"
                execute_query(query, (key, value, description))
            
            return True
        except Exception as e:
            print(f"Error setting value: {e}")
            return False
    
    @staticmethod
    def get_all_settings() -> List[Dict]:
        """Get all settings"""
        query = "SELECT key, value, description FROM settings ORDER BY key"
        return execute_query_dict(query, fetch='all') or []
    
    @staticmethod
    def delete_setting(key: str) -> bool:
        """
        Delete a setting
        
        Args:
            key: Setting key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "DELETE FROM settings WHERE key = ?"
            execute_query(query, (key,))
            return True
        except Exception as e:
            print(f"Error deleting setting: {e}")
            return False
    
    @staticmethod
    def get_tax_rate() -> float:
        """Get the current tax rate"""
        try:
            rate_str = SettingsManager.get_setting('tax_rate')
            return float(rate_str) if rate_str else 0.08
        except (ValueError, TypeError):
            return 0.08
    
    @staticmethod
    def set_tax_rate(rate: float) -> bool:
        """Set the tax rate"""
        return SettingsManager.set_setting('tax_rate', str(rate), 'Sales tax rate')
    
    @staticmethod
    def get_receipt_header() -> str:
        """Get the receipt header text"""
        return SettingsManager.get_setting('receipt_header') or 'Your Business Name'
    
    @staticmethod
    def set_receipt_header(header: str) -> bool:
        """Set the receipt header text"""
        return SettingsManager.set_setting('receipt_header', header, 'Receipt header text')
    
    @staticmethod
    def get_receipt_footer() -> str:
        """Get the receipt footer text"""
        return SettingsManager.get_setting('receipt_footer') or 'Thank you for your business!'
    
    @staticmethod
    def set_receipt_footer(footer: str) -> bool:
        """Set the receipt footer text"""
        return SettingsManager.set_setting('receipt_footer', footer, 'Receipt footer text')
    
    @staticmethod
    def get_company_info() -> Dict[str, str]:
        """Get company information"""
        return {
            'name': SettingsManager.get_setting('company_name') or 'Your Business Name',
            'address': SettingsManager.get_setting('company_address') or '123 Business St, City, State 12345',
            'phone': SettingsManager.get_setting('company_phone') or '(555) 123-4567',
            'email': SettingsManager.get_setting('company_email') or '',
            'website': SettingsManager.get_setting('company_website') or ''
        }
    
    @staticmethod
    def set_company_info(name: str = None, address: str = None, phone: str = None, 
                        email: str = None, website: str = None) -> bool:
        """Set company information"""
        try:
            success = True
            if name is not None:
                success &= SettingsManager.set_setting('company_name', name, 'Company name')
            if address is not None:
                success &= SettingsManager.set_setting('company_address', address, 'Company address')
            if phone is not None:
                success &= SettingsManager.set_setting('company_phone', phone, 'Company phone')
            if email is not None:
                success &= SettingsManager.set_setting('company_email', email, 'Company email')
            if website is not None:
                success &= SettingsManager.set_setting('company_website', website, 'Company website')
            return success
        except Exception as e:
            print(f"Error setting company info: {e}")
            return False
    
    @staticmethod
    def get_printer_settings() -> Dict[str, str]:
        """Get printer settings"""
        return {
            'receipt_printer': SettingsManager.get_setting('receipt_printer') or '',
            'kitchen_printer': SettingsManager.get_setting('kitchen_printer') or '',
            'receipt_width': SettingsManager.get_setting('receipt_width') or '80',
            'auto_print_receipt': SettingsManager.get_setting('auto_print_receipt') or 'false',
            'auto_print_kitchen': SettingsManager.get_setting('auto_print_kitchen') or 'false'
        }
    
    @staticmethod
    def set_printer_settings(receipt_printer: str = None, kitchen_printer: str = None,
                           receipt_width: str = None, auto_print_receipt: bool = None,
                           auto_print_kitchen: bool = None) -> bool:
        """Set printer settings"""
        try:
            success = True
            if receipt_printer is not None:
                success &= SettingsManager.set_setting('receipt_printer', receipt_printer, 'Receipt printer name')
            if kitchen_printer is not None:
                success &= SettingsManager.set_setting('kitchen_printer', kitchen_printer, 'Kitchen printer name')
            if receipt_width is not None:
                success &= SettingsManager.set_setting('receipt_width', receipt_width, 'Receipt width in characters')
            if auto_print_receipt is not None:
                success &= SettingsManager.set_setting('auto_print_receipt', str(auto_print_receipt).lower(), 'Auto print receipts')
            if auto_print_kitchen is not None:
                success &= SettingsManager.set_setting('auto_print_kitchen', str(auto_print_kitchen).lower(), 'Auto print kitchen tickets')
            return success
        except Exception as e:
            print(f"Error setting printer settings: {e}")
            return False
