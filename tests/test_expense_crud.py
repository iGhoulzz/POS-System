"""
Unit tests for Expense CRUD operations.
"""

import pytest
from db.db_utils import execute_query, execute_query_dict
from logic.report_generator import ReportGenerator


class TestExpenseCreate:
    def test_insert_expense(self, admin_user_id):
        execute_query(
            """INSERT INTO expenses (description, amount, category, date, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            ("Flour bags", 50.00, "Supplies", "2026-02-20", admin_user_id),
        )
        row = execute_query_dict(
            "SELECT * FROM expenses WHERE description = ?", ("Flour bags",), "one"
        )
        assert row is not None
        assert row["amount"] == 50.00
        assert row["category"] == "Supplies"

    def test_insert_multiple_expenses(self, admin_user_id):
        for i in range(3):
            execute_query(
                """INSERT INTO expenses (description, amount, category, date, created_by)
                   VALUES (?, ?, ?, ?, ?)""",
                (f"Item {i}", 10.0 * (i + 1), "General", "2026-02-20", admin_user_id),
            )
        rows = execute_query_dict(
            "SELECT * FROM expenses WHERE category = ?", ("General",), "all"
        )
        assert len(rows) >= 3


class TestExpenseRead:
    def test_read_expenses_by_date(self, admin_user_id):
        execute_query(
            """INSERT INTO expenses (description, amount, category, date, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            ("Milk", 12.00, "Supplies", "2026-02-20", admin_user_id),
        )
        rows = execute_query_dict(
            "SELECT * FROM expenses WHERE date = ?", ("2026-02-20",), "all"
        )
        assert len(rows) >= 1

    def test_expense_report(self, admin_user_id):
        execute_query(
            """INSERT INTO expenses (description, amount, category, date, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            ("Sugar", 8.50, "Supplies", "2026-02-20", admin_user_id),
        )
        report = ReportGenerator.get_expense_report("2026-02-20", "2026-02-20")
        assert report["totals"]["total_count"] >= 1
        assert report["totals"]["total_amount"] >= 8.50


class TestExpenseUpdate:
    def test_update_amount(self, admin_user_id):
        execute_query(
            """INSERT INTO expenses (description, amount, category, date, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            ("Napkins", 5.00, "Supplies", "2026-02-20", admin_user_id),
        )
        row = execute_query_dict(
            "SELECT id FROM expenses WHERE description = ?", ("Napkins",), "one"
        )
        execute_query(
            "UPDATE expenses SET amount = ? WHERE id = ?",
            (7.50, row["id"]),
        )
        updated = execute_query_dict(
            "SELECT * FROM expenses WHERE id = ?", (row["id"],), "one"
        )
        assert updated["amount"] == 7.50


class TestExpenseDelete:
    def test_delete_expense(self, admin_user_id):
        execute_query(
            """INSERT INTO expenses (description, amount, category, date, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            ("Straws", 3.00, "Supplies", "2026-02-20", admin_user_id),
        )
        row = execute_query_dict(
            "SELECT id FROM expenses WHERE description = ?", ("Straws",), "one"
        )
        execute_query("DELETE FROM expenses WHERE id = ?", (row["id"],))
        deleted = execute_query_dict(
            "SELECT * FROM expenses WHERE id = ?", (row["id"],), "one"
        )
        assert deleted is None
