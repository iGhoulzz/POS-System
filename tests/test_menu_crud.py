"""
Unit tests for menu item and category CRUD operations.
"""

import pytest
from db.db_utils import execute_query, execute_query_dict


# ---------------------------------------------------------------------------
# Category CRUD
# ---------------------------------------------------------------------------

class TestCategoryCreate:
    def test_insert_category(self):
        execute_query(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            ("Appetizers", "Starters"),
        )
        row = execute_query_dict(
            "SELECT * FROM categories WHERE name = ?", ("Appetizers",), "one"
        )
        assert row is not None
        assert row["description"] == "Starters"
        assert row["is_active"] == 1

    def test_duplicate_category_name_fails(self):
        execute_query(
            "INSERT INTO categories (name, description) VALUES (?, ?)",
            ("Desserts", "Sweet things"),
        )
        with pytest.raises(Exception):
            execute_query(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                ("Desserts", "Duplicated"),
            )


class TestCategoryRead:
    def test_list_categories(self, sample_category):
        rows = execute_query_dict(
            "SELECT * FROM categories WHERE is_active = 1", fetch="all"
        )
        assert any(r["name"] == "Beverages" for r in rows)


class TestCategoryUpdate:
    def test_update_category_name(self, sample_category):
        execute_query(
            "UPDATE categories SET name = ? WHERE id = ?",
            ("Drinks", sample_category),
        )
        row = execute_query_dict(
            "SELECT * FROM categories WHERE id = ?", (sample_category,), "one"
        )
        assert row["name"] == "Drinks"


class TestCategoryDelete:
    def test_soft_delete_category(self, sample_category):
        execute_query(
            "UPDATE categories SET is_active = 0 WHERE id = ?",
            (sample_category,),
        )
        row = execute_query_dict(
            "SELECT * FROM categories WHERE id = ?", (sample_category,), "one"
        )
        assert row["is_active"] == 0


# ---------------------------------------------------------------------------
# Menu Item CRUD
# ---------------------------------------------------------------------------

class TestMenuItemCreate:
    def test_insert_menu_item(self, sample_category):
        execute_query(
            """INSERT INTO menu_items
               (name, description, cost_price, price, category_id, is_active, preparation_time)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("Espresso", "Strong coffee", 1.00, 3.00, sample_category, 1, 3),
        )
        row = execute_query_dict(
            "SELECT * FROM menu_items WHERE name = ?", ("Espresso",), "one"
        )
        assert row is not None
        assert row["price"] == 3.00
        assert row["cost_price"] == 1.00
        assert row["preparation_time"] == 3


class TestMenuItemRead:
    def test_read_with_category_join(self, sample_menu_item, sample_category):
        row = execute_query_dict(
            """SELECT mi.*, c.name as category_name
               FROM menu_items mi
               JOIN categories c ON mi.category_id = c.id
               WHERE mi.id = ?""",
            (sample_menu_item,),
            "one",
        )
        assert row["category_name"] == "Beverages"
        assert row["name"] == "Latte"


class TestMenuItemUpdate:
    def test_update_price(self, sample_menu_item):
        execute_query(
            "UPDATE menu_items SET price = ? WHERE id = ?",
            (5.99, sample_menu_item),
        )
        row = execute_query_dict(
            "SELECT * FROM menu_items WHERE id = ?", (sample_menu_item,), "one"
        )
        assert row["price"] == 5.99

    def test_update_preparation_time(self, sample_menu_item):
        execute_query(
            "UPDATE menu_items SET preparation_time = ? WHERE id = ?",
            (10, sample_menu_item),
        )
        row = execute_query_dict(
            "SELECT * FROM menu_items WHERE id = ?", (sample_menu_item,), "one"
        )
        assert row["preparation_time"] == 10


class TestMenuItemDelete:
    def test_soft_delete_menu_item(self, sample_menu_item):
        execute_query(
            "UPDATE menu_items SET is_active = 0 WHERE id = ?",
            (sample_menu_item,),
        )
        row = execute_query_dict(
            "SELECT * FROM menu_items WHERE id = ?", (sample_menu_item,), "one"
        )
        assert row["is_active"] == 0
