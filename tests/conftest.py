"""
Shared pytest fixtures for the POS System test suite.
"""

import os
import sys
import sqlite3
import shutil
import tempfile

import pytest

# Ensure project root is on the path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture(autouse=True)
def _isolated_db(tmp_path, monkeypatch):
    """
    Redirect all database operations to a temporary directory so that
    tests never touch the real database.  The temporary DB is initialised
    with the full schema before every test and destroyed afterwards.
    """
    db_dir = str(tmp_path)
    db_name = "test_pos.db"

    # Patch both config and every module that imported the values at load time
    monkeypatch.setattr("config.DATABASE_PATH", db_dir)
    monkeypatch.setattr("config.DATABASE_NAME", db_name)
    monkeypatch.setattr("db.db_utils.DATABASE_PATH", db_dir)
    monkeypatch.setattr("db.db_utils.DATABASE_NAME", db_name)
    monkeypatch.setattr("db.init_db.DATABASE_PATH", db_dir)
    monkeypatch.setattr("db.init_db.DATABASE_NAME", db_name)

    from db.init_db import initialize_database
    initialize_database()

    yield  # run the test

    # Cleanup is automatic because tmp_path is removed by pytest


@pytest.fixture()
def db_conn(tmp_path):
    """Return a dict-row connection to the test database."""
    from db.db_utils import get_db_connection_with_dict
    conn = get_db_connection_with_dict()
    yield conn
    conn.close()


@pytest.fixture()
def sample_category():
    """Insert a sample category and return its id."""
    from db.db_utils import execute_query
    execute_query(
        "INSERT INTO categories (name, description) VALUES (?, ?)",
        ("Beverages", "Hot and cold drinks"),
    )
    row = execute_query(
        "SELECT id FROM categories WHERE name = ?", ("Beverages",), "one"
    )
    return row[0]


@pytest.fixture()
def sample_menu_item(sample_category):
    """Insert a sample menu item and return its id."""
    from db.db_utils import execute_query
    execute_query(
        """INSERT INTO menu_items
           (name, description, cost_price, price, category_id, is_active, preparation_time)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        ("Latte", "Coffee with milk", 1.50, 4.50, sample_category, 1, 5),
    )
    row = execute_query(
        "SELECT id FROM menu_items WHERE name = ?", ("Latte",), "one"
    )
    return row[0]


@pytest.fixture()
def admin_user_id():
    """Return the id of the default admin user created during DB init."""
    from db.db_utils import execute_query
    row = execute_query(
        "SELECT id FROM users WHERE username = ?", ("admin",), "one"
    )
    return row[0]


@pytest.fixture(autouse=True)
def _reset_event_bus():
    """Reset the EventBus singleton between tests."""
    from logic.event_bus import EventBus
    EventBus.reset_instance()
    yield
    EventBus.reset_instance()
