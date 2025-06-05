"""
User management logic
"""

import hashlib
from typing import Optional, List, Dict
from db.db_utils import execute_query_dict, execute_query

class UserManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user
        
        Args:
            username: Username
            password: Plain text password
        
        Returns:
            User dictionary if authenticated, None otherwise
        """
        password_hash = UserManager.hash_password(password)
        query = '''
            SELECT id, username, role, full_name, email, last_login, is_active
            FROM users
            WHERE username = ? AND password_hash = ? AND is_active = 1
        '''
        user = execute_query_dict(query, (username, password_hash), 'one')

        if user:
            # Update last_login timestamp
            execute_query(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user['id'],)
            )
        return user
    
    @staticmethod
    def get_all_users() -> List[Dict]:
        """Get all users"""
        query = '''
            SELECT id, username, role, full_name, email, last_login, created_at, is_active
            FROM users
            ORDER BY full_name
        '''
        return execute_query_dict(query, fetch='all') or []
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        query = '''
            SELECT id, username, role, full_name, email, last_login, created_at, is_active
            FROM users
            WHERE id = ?
        '''
        return execute_query_dict(query, (user_id,), 'one')
    
    @staticmethod
    def create_user(
        username: str,
        password: str,
        role: str,
        full_name: str,
        email: str = None,
        is_active: bool = True
    ) -> bool:
        """
        Create a new user
        
        Args:
            username: Username
            password: Plain text password
            role: User role ('admin', 'cashier', 'kitchen')
            full_name: Full name
            email: Email address (optional)
            is_active: Active status, defaults to True
        
        Returns:
            True if successful, False otherwise
        """
        try:
            password_hash = UserManager.hash_password(password)
            query = '''
                INSERT INTO users (username, password_hash, role, full_name, email, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            execute_query(
                query,
                (username, password_hash, role, full_name, email, int(is_active))
            )
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    @staticmethod
    def update_user(
        user_id: int,
        username: str = None,
        password: str = None,
        role: str = None,
        full_name: str = None,
        email: str = None,
        is_active: bool = None
    ) -> bool:
        """
        Update user information
        
        Args:
            user_id: User ID
            username: New username (optional)
            password: New password (optional)
            role: New role (optional)
            full_name: New full name (optional)
            email: New email address (optional)
            is_active: New active status (optional)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            updates = []
            params = []
            
            if username is not None:
                updates.append("username = ?")
                params.append(username)
            
            if password is not None:
                updates.append("password_hash = ?")
                params.append(UserManager.hash_password(password))
            
            if role is not None:
                updates.append("role = ?")
                params.append(role)
            
            if full_name is not None:
                updates.append("full_name = ?")
                params.append(full_name)

            if email is not None:
                updates.append("email = ?")
                params.append(email)
            
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(is_active)
            
            if not updates:
                return False
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            execute_query(query, tuple(params))
            return True
        
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """
        Deactivate a user (soft delete)
        
        Args:
            user_id: User ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            query = "UPDATE users SET is_active = 0 WHERE id = ?"
            execute_query(query, (user_id,))
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
