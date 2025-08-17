"""
Database utility functions
"""

import sqlite3
import os
from config import DATABASE_NAME, DATABASE_PATH
from typing import List, Dict, Any, Optional

def get_db_connection():
    """Get a database connection with foreign keys enabled and timeout settings"""
    db_file = os.path.join(DATABASE_PATH, DATABASE_NAME)
    
    # Check if database file exists
    if not os.path.exists(db_file):
        raise sqlite3.OperationalError(f"Database file not found: {db_file}")
    
    try:
        # Set timeout to 10 seconds to prevent infinite hanging
        conn = sqlite3.connect(db_file, timeout=10.0)
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        # Set journal mode for better performance and reliability
        conn.execute("PRAGMA journal_mode = WAL")
        # Set a reasonable busy timeout
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(f"Database connection failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected database error: {str(e)}")

def execute_query(query: str, params: tuple = None, fetch: str = None) -> Any:
    """
    Execute a database query
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: 'one', 'all', or None
    
    Returns:
        Query result, rowcount for DELETE/UPDATE operations, or None
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            # For DELETE, UPDATE, INSERT operations, return the number of affected rows
            query_type = query.strip().upper().split()[0]
            if query_type in ('DELETE', 'UPDATE', 'INSERT'):
                result = cursor.rowcount
            else:
                result = None
        
        conn.commit()
        return result
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def dict_factory(cursor, row):
    """Row factory to return dictionaries instead of tuples"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db_connection_with_dict():
    """Get a database connection that returns dictionaries with foreign keys enabled"""
    conn = get_db_connection()
    conn.row_factory = dict_factory
    return conn

def execute_query_dict(query: str, params: tuple = None, fetch: str = None) -> Any:
    """
    Execute a database query and return dictionaries
    
    Args:
        query: SQL query string
        params: Query parameters
        fetch: 'one', 'all', or None
    
    Returns:
        Query result as dictionary/list of dictionaries, rowcount for DELETE/UPDATE operations, or None
    """
    conn = None
    try:
        conn = get_db_connection_with_dict()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            # For DELETE, UPDATE, INSERT operations, return the number of affected rows
            query_type = query.strip().upper().split()[0]
            if query_type in ('DELETE', 'UPDATE', 'INSERT'):
                result = cursor.rowcount
            else:
                result = None
        
        conn.commit()
        return result
    
    except sqlite3.OperationalError as e:
        if conn:
            conn.rollback()
        if "database is locked" in str(e).lower():
            raise sqlite3.OperationalError("Database is busy. Please try again in a moment.")
        elif "timeout" in str(e).lower():
            raise sqlite3.OperationalError("Database operation timed out. Please check your connection.")
        else:
            raise sqlite3.OperationalError(f"Database error: {str(e)}")
    except sqlite3.DatabaseError as e:
        if conn:
            conn.rollback()
        raise sqlite3.DatabaseError(f"Database error: {str(e)}")
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Unexpected database error: {str(e)}")
    finally:
        if conn:
            conn.close()

def backup_database(backup_path: str) -> bool:
    """
    Create a backup of the database
    
    Args:
        backup_path: Path where to save the backup
    
    Returns:
        True if successful, False otherwise
    """
    try:
        source_conn = get_db_connection()
        backup_conn = sqlite3.connect(backup_path)
        source_conn.backup(backup_conn)
        source_conn.close()
        backup_conn.close()
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False
