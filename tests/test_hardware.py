"""
Unit tests for the hardware abstraction layer.

Validates printers, displays, and the HardwareManager, including
automatic event-driven behaviour (e.g. auto-print on order_completed).
"""

import os
import pytest
from logic.event_bus import EventBus
from logic.hardware import (
    ReceiptPrinter,
    KitchenPrinter,
    KitchenDisplaySystem,
    CustomerDisplay,
    HardwareManager,
)


# ---------------------------------------------------------------------------
# ReceiptPrinter
# ---------------------------------------------------------------------------

class TestReceiptPrinter:
    def test_connect_creates_output_dir(self, tmp_path):
        out = str(tmp_path / "receipts_test")
        printer = ReceiptPrinter(output_dir=out)
        assert printer.connect() is True
        assert printer.is_connected
        assert os.path.isdir(out)

    def test_print_content_creates_file(self, tmp_path):
        out = str(tmp_path / "rp")
        printer = ReceiptPrinter(output_dir=out)
        printer.connect()
        assert printer.print_content("Hello receipt") is True
        files = os.listdir(out)
        assert len(files) == 1
        content = open(os.path.join(out, files[0])).read()
        assert "Hello receipt" in content

    def test_print_content_fails_when_disconnected(self, tmp_path):
        printer = ReceiptPrinter(output_dir=str(tmp_path))
        assert printer.print_content("nope") is False

    def test_disconnect(self, tmp_path):
        printer = ReceiptPrinter(output_dir=str(tmp_path))
        printer.connect()
        printer.disconnect()
        assert printer.is_connected is False

    def test_auto_print_on_order_completed(self, tmp_path):
        out = str(tmp_path / "auto_rp")
        printer = ReceiptPrinter(output_dir=out)
        printer.connect()
        bus = EventBus.get_instance()
        bus.publish("order_completed", {
            "order_id": 1,
            "receipt_text": "*** RECEIPT ***\nTotal: $10.00",
        })
        files = os.listdir(out)
        assert len(files) == 1


# ---------------------------------------------------------------------------
# KitchenPrinter
# ---------------------------------------------------------------------------

class TestKitchenPrinter:
    def test_connect_and_print(self, tmp_path):
        out = str(tmp_path / "kp")
        printer = KitchenPrinter(output_dir=out)
        printer.connect()
        assert printer.print_content("KITCHEN TICKET") is True
        files = os.listdir(out)
        assert len(files) == 1

    def test_format_kitchen_ticket(self, tmp_path):
        printer = KitchenPrinter(output_dir=str(tmp_path))
        ticket = printer.format_kitchen_ticket({
            "order_number": "ORD-001",
            "order_type": "dine_in",
            "items": [
                {"item_name": "Latte", "quantity": 2, "special_instructions": "Extra hot"},
                {"item_name": "Muffin", "quantity": 1},
            ],
        })
        assert "ORD-001" in ticket
        assert "2x  Latte" in ticket
        assert "Extra hot" in ticket
        assert "1x  Muffin" in ticket

    def test_auto_print_on_order_created(self, tmp_path):
        out = str(tmp_path / "auto_kp")
        printer = KitchenPrinter(output_dir=out)
        printer.connect()
        bus = EventBus.get_instance()
        bus.publish("order_created", {
            "order_id": 2,
            "order_number": "ORD-002",
            "order_type": "takeout",
            "items": [{"item_name": "Espresso", "quantity": 1}],
        })
        files = os.listdir(out)
        assert len(files) == 1


# ---------------------------------------------------------------------------
# KitchenDisplaySystem
# ---------------------------------------------------------------------------

class TestKitchenDisplaySystem:
    def test_connect(self):
        kds = KitchenDisplaySystem()
        assert kds.connect() is True
        assert kds.is_connected

    def test_order_added_on_event(self):
        kds = KitchenDisplaySystem()
        kds.connect()
        bus = EventBus.get_instance()
        bus.publish("order_created", {
            "order_id": 10,
            "order_number": "ORD-010",
            "order_type": "dine_in",
            "items": [{"item_name": "Burger", "quantity": 1}],
        })
        orders = kds.get_active_orders()
        assert len(orders) == 1
        assert orders[0]["order_number"] == "ORD-010"
        assert orders[0]["status"] == "pending"

    def test_status_update_propagates(self):
        kds = KitchenDisplaySystem()
        kds.connect()
        bus = EventBus.get_instance()
        bus.publish("order_created", {
            "order_id": 11,
            "order_number": "ORD-011",
            "order_type": "dine_in",
            "items": [],
        })
        bus.publish("order_status_changed", {
            "order_id": 11,
            "new_status": "preparing",
        })
        orders = kds.get_active_orders()
        assert orders[0]["status"] == "preparing"

    def test_completed_order_removed(self):
        kds = KitchenDisplaySystem()
        kds.connect()
        bus = EventBus.get_instance()
        bus.publish("order_created", {
            "order_id": 12,
            "order_number": "ORD-012",
            "order_type": "takeout",
            "items": [],
        })
        bus.publish("order_completed", {"order_id": 12})
        assert len(kds.get_active_orders()) == 0

    def test_cancelled_order_removed(self):
        kds = KitchenDisplaySystem()
        kds.connect()
        bus = EventBus.get_instance()
        bus.publish("order_created", {
            "order_id": 13,
            "order_number": "ORD-013",
            "order_type": "dine_in",
            "items": [],
        })
        bus.publish("order_cancelled", {"order_id": 13})
        assert len(kds.get_active_orders()) == 0


# ---------------------------------------------------------------------------
# CustomerDisplay
# ---------------------------------------------------------------------------

class TestCustomerDisplay:
    def test_connect(self):
        cd = CustomerDisplay()
        assert cd.connect() is True

    def test_shows_preparing_message(self):
        cd = CustomerDisplay()
        cd.connect()
        bus = EventBus.get_instance()
        bus.publish("order_status_changed", {
            "order_number": "ORD-020",
            "new_status": "preparing",
        })
        assert "prepared" in cd.current_content.get("message", "").lower()

    def test_shows_ready_message(self):
        cd = CustomerDisplay()
        cd.connect()
        bus = EventBus.get_instance()
        bus.publish("order_status_changed", {
            "order_number": "ORD-021",
            "new_status": "ready",
        })
        assert "ready" in cd.current_content.get("message", "").lower()

    def test_shows_completed_message(self):
        cd = CustomerDisplay()
        cd.connect()
        bus = EventBus.get_instance()
        bus.publish("order_completed", {"order_number": "ORD-022"})
        assert "complete" in cd.current_content.get("message", "").lower()


# ---------------------------------------------------------------------------
# HardwareManager
# ---------------------------------------------------------------------------

class TestHardwareManager:
    def test_initialize_creates_devices(self):
        hm = HardwareManager()
        hm.initialize()
        assert hm.receipt_printer is not None
        assert hm.kitchen_printer is not None
        assert hm.kitchen_display is not None
        assert hm.customer_display is not None

    def test_connect_all(self, tmp_path):
        hm = HardwareManager()
        hm.initialize(output_dir=str(tmp_path))
        results = hm.connect_all()
        assert all(v is True for v in results.values())

    def test_disconnect_all(self, tmp_path):
        hm = HardwareManager()
        hm.initialize(output_dir=str(tmp_path))
        hm.connect_all()
        hm.disconnect_all()
        status = hm.get_all_status()
        assert all(s["is_connected"] is False for s in status.values())

    def test_get_all_status(self, tmp_path):
        hm = HardwareManager()
        hm.initialize(output_dir=str(tmp_path))
        hm.connect_all()
        status = hm.get_all_status()
        assert "receipt_printer" in status
        assert "kitchen_printer" in status
        assert "kitchen_display" in status
        assert "customer_display" in status


# ---------------------------------------------------------------------------
# End-to-end: order lifecycle through hardware
# ---------------------------------------------------------------------------

class TestHardwareOrderLifecycle:
    """Simulate a full order lifecycle and verify all hardware reacts."""

    def test_full_lifecycle(self, tmp_path):
        hm = HardwareManager()
        hm.initialize(output_dir=str(tmp_path))
        hm.connect_all()
        bus = EventBus.get_instance()

        # 1. Order created  → kitchen printer + kitchen display
        bus.publish("order_created", {
            "order_id": 100,
            "order_number": "ORD-100",
            "order_type": "dine_in",
            "items": [{"item_name": "Pizza", "quantity": 1}],
        })
        assert len(hm.kitchen_display.get_active_orders()) == 1
        kitchen_files = [f for f in os.listdir(str(tmp_path)) if f.startswith("kitchen_")]
        assert len(kitchen_files) == 1

        # 2. Status → preparing  → customer display updates
        bus.publish("order_status_changed", {
            "order_id": 100,
            "order_number": "ORD-100",
            "new_status": "preparing",
        })
        assert hm.kitchen_display.get_active_orders()[0]["status"] == "preparing"
        assert "prepared" in hm.customer_display.current_content.get("message", "").lower()

        # 3. Status → ready  → customer display updates
        bus.publish("order_status_changed", {
            "order_id": 100,
            "order_number": "ORD-100",
            "new_status": "ready",
        })
        assert "ready" in hm.customer_display.current_content.get("message", "").lower()

        # 4. Order completed → receipt printer + removed from kitchen display
        bus.publish("order_completed", {
            "order_id": 100,
            "order_number": "ORD-100",
            "receipt_text": "RECEIPT for ORD-100\nTotal: $15.00",
        })
        assert len(hm.kitchen_display.get_active_orders()) == 0
        receipt_files = [f for f in os.listdir(str(tmp_path)) if f.startswith("receipt_")]
        assert len(receipt_files) == 1

        hm.disconnect_all()
