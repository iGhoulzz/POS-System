"""
Unit tests for Order CRUD operations and the complete order lifecycle.
"""

import pytest
from logic.order_manager import OrderManager
from db.db_utils import execute_query, execute_query_dict


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_order_items(menu_item_id):
    """Return a minimal list of order items for testing."""
    return [
        {
            "menu_item_id": menu_item_id,
            "quantity": 2,
            "unit_price": 4.50,
            "special_instructions": "Extra hot",
        }
    ]


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------

class TestOrderCreate:
    def test_create_order_success(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Alice", "dine_in", items, "cash", admin_user_id
        )
        assert result is not None
        assert "order_id" in result
        assert "order_number" in result
        assert result["order_number"].startswith("ORD-")

    def test_create_order_empty_items_returns_none(self, admin_user_id):
        result = OrderManager.create_order(
            "Bob", "takeout", [], "card", admin_user_id
        )
        assert result is None

    def test_create_order_calculates_totals(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Carol", "delivery", items, "card", admin_user_id, tax_rate=0.10
        )
        order = OrderManager.get_order_by_id(result["order_id"])
        expected_subtotal = 2 * 4.50
        expected_tax = expected_subtotal * 0.10
        assert abs(order["total_amount"] - (expected_subtotal + expected_tax)) < 0.01
        assert abs(order["tax_amount"] - expected_tax) < 0.01

    def test_create_order_default_status_is_pending(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Dave", "dine_in", items, "cash", admin_user_id
        )
        order = OrderManager.get_order_by_id(result["order_id"])
        assert order["status"] == "pending"


class TestOrderRead:
    def test_get_order_by_id(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Eve", "takeout", items, "cash", admin_user_id
        )
        order = OrderManager.get_order_by_id(result["order_id"])
        assert order is not None
        assert order["customer_name"] == "Eve"

    def test_get_order_by_invalid_id(self):
        assert OrderManager.get_order_by_id(99999) is None

    def test_get_order_items(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Frank", "dine_in", items, "cash", admin_user_id
        )
        order_items = OrderManager.get_order_items(result["order_id"])
        assert len(order_items) == 1
        assert order_items[0]["quantity"] == 2
        assert order_items[0]["item_name"] == "Latte"

    def test_get_pending_orders(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        OrderManager.create_order("Grace", "dine_in", items, "cash", admin_user_id)
        pending = OrderManager.get_pending_orders()
        assert len(pending) >= 1


class TestOrderUpdate:
    def test_update_status_to_preparing(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Heidi", "dine_in", items, "cash", admin_user_id
        )
        assert OrderManager.update_order_status(result["order_id"], "preparing") is True
        order = OrderManager.get_order_by_id(result["order_id"])
        assert order["status"] == "preparing"

    def test_update_status_to_completed_sets_timestamp(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        result = OrderManager.create_order(
            "Ivan", "dine_in", items, "cash", admin_user_id
        )
        OrderManager.update_order_status(result["order_id"], "completed")
        order = OrderManager.get_order_by_id(result["order_id"])
        assert order["status"] == "completed"
        assert order["completed_at"] is not None


class TestOrderSalesSummary:
    def test_sales_summary_empty_range(self):
        summary = OrderManager.get_sales_summary("2000-01-01", "2000-01-02")
        assert summary["total_orders"] == 0

    def test_sales_summary_includes_created_order(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        OrderManager.create_order("Judy", "dine_in", items, "cash", admin_user_id)
        from datetime import date
        today = date.today().isoformat()
        summary = OrderManager.get_sales_summary(today, today)
        assert summary["total_orders"] >= 1


# ---------------------------------------------------------------------------
# Order lifecycle / status transition tests
# ---------------------------------------------------------------------------

class TestOrderLifecycle:
    """
    Verify the full order status lifecycle:
        pending → preparing → ready → completed
    and the cancellation path:
        pending → cancelled
    """

    def _create_test_order(self, sample_menu_item, admin_user_id):
        items = _make_order_items(sample_menu_item)
        return OrderManager.create_order(
            "Lifecycle Test", "dine_in", items, "cash", admin_user_id
        )

    def test_full_lifecycle(self, sample_menu_item, admin_user_id):
        result = self._create_test_order(sample_menu_item, admin_user_id)
        oid = result["order_id"]

        for status in ("preparing", "ready", "completed"):
            assert OrderManager.update_order_status(oid, status) is True
            order = OrderManager.get_order_by_id(oid)
            assert order["status"] == status

    def test_cancel_from_pending(self, sample_menu_item, admin_user_id):
        result = self._create_test_order(sample_menu_item, admin_user_id)
        oid = result["order_id"]
        assert OrderManager.update_order_status(oid, "cancelled") is True
        order = OrderManager.get_order_by_id(oid)
        assert order["status"] == "cancelled"

    def test_cancelled_excluded_from_pending(self, sample_menu_item, admin_user_id):
        result = self._create_test_order(sample_menu_item, admin_user_id)
        OrderManager.update_order_status(result["order_id"], "cancelled")
        pending = OrderManager.get_pending_orders()
        ids = [o["id"] for o in pending]
        assert result["order_id"] not in ids

    def test_completed_excluded_from_pending(self, sample_menu_item, admin_user_id):
        result = self._create_test_order(sample_menu_item, admin_user_id)
        OrderManager.update_order_status(result["order_id"], "completed")
        pending = OrderManager.get_pending_orders()
        ids = [o["id"] for o in pending]
        assert result["order_id"] not in ids
