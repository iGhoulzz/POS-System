"""
Hardware abstraction layer for POS peripherals.

Provides abstract interfaces and concrete implementations for:
    - Receipt printers (customer invoices)
    - Kitchen printers (order tickets)
    - Customer-facing displays (order status screens)
    - Kitchen display systems (upcoming orders)
    - Kiosk screens

Each hardware component auto-subscribes to relevant EventBus events,
enabling plug-and-play integration. For production desktop deployment,
concrete implementations delegate to OS-level printing and display APIs.
"""

import abc
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

from logic.event_bus import EventBus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Abstract base classes
# ---------------------------------------------------------------------------

class BasePrinter(abc.ABC):
    """Abstract interface for all printer types."""

    def __init__(self, printer_name: str = ""):
        self.printer_name = printer_name
        self.is_connected = False

    @abc.abstractmethod
    def connect(self) -> bool:
        """Establish connection to the printer hardware."""

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the printer hardware."""

    @abc.abstractmethod
    def print_content(self, content: str) -> bool:
        """Send content to the printer."""

    def get_status(self) -> Dict[str, Any]:
        """Return current printer status."""
        return {
            "printer_name": self.printer_name,
            "is_connected": self.is_connected,
        }


class BaseDisplay(abc.ABC):
    """Abstract interface for all display types."""

    def __init__(self, display_name: str = ""):
        self.display_name = display_name
        self.is_connected = False

    @abc.abstractmethod
    def connect(self) -> bool:
        """Establish connection to the display hardware."""

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the display hardware."""

    @abc.abstractmethod
    def update_content(self, content: Dict[str, Any]) -> bool:
        """Push content to the display."""

    def get_status(self) -> Dict[str, Any]:
        """Return current display status."""
        return {
            "display_name": self.display_name,
            "is_connected": self.is_connected,
        }


# ---------------------------------------------------------------------------
# Concrete printer implementations
# ---------------------------------------------------------------------------

class ReceiptPrinter(BasePrinter):
    """
    Receipt / invoice printer for customer-facing output.

    In production, delegates to the OS print subsystem or python-escpos
    for thermal printers.  Falls back to file-based output for testing
    or when no hardware is available.
    """

    def __init__(self, printer_name: str = "", output_dir: str = "receipts"):
        super().__init__(printer_name)
        self.output_dir = output_dir
        self._event_bus = EventBus.get_instance()
        self._event_bus.subscribe("order_completed", self._on_order_completed)

    def connect(self) -> bool:
        os.makedirs(self.output_dir, exist_ok=True)
        self.is_connected = True
        logger.info("ReceiptPrinter connected (output_dir=%s)", self.output_dir)
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("ReceiptPrinter disconnected")

    def print_content(self, content: str) -> bool:
        if not self.is_connected:
            logger.warning("ReceiptPrinter not connected")
            return False
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.output_dir, f"receipt_{timestamp}.txt")
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            logger.info("Receipt saved to %s", path)
            return True
        except OSError as exc:
            logger.error("Failed to write receipt: %s", exc)
            return False

    # -- event handler -------------------------------------------------------
    def _on_order_completed(self, data: Dict[str, Any]) -> None:
        """Auto-print receipt when an order is completed."""
        content = data.get("receipt_text", "")
        if content:
            self.print_content(content)


class KitchenPrinter(BasePrinter):
    """
    Kitchen ticket printer for back-of-house order tickets.

    Subscribes to ``order_created`` so that a kitchen ticket is printed
    automatically whenever a new order is placed.
    """

    def __init__(self, printer_name: str = "", output_dir: str = "receipts"):
        super().__init__(printer_name)
        self.output_dir = output_dir
        self._event_bus = EventBus.get_instance()
        self._event_bus.subscribe("order_created", self._on_order_created)

    def connect(self) -> bool:
        os.makedirs(self.output_dir, exist_ok=True)
        self.is_connected = True
        logger.info("KitchenPrinter connected (output_dir=%s)", self.output_dir)
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("KitchenPrinter disconnected")

    def print_content(self, content: str) -> bool:
        if not self.is_connected:
            logger.warning("KitchenPrinter not connected")
            return False
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(self.output_dir, f"kitchen_{timestamp}.txt")
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            logger.info("Kitchen ticket saved to %s", path)
            return True
        except OSError as exc:
            logger.error("Failed to write kitchen ticket: %s", exc)
            return False

    def format_kitchen_ticket(self, order_data: Dict[str, Any]) -> str:
        """Format an order into a kitchen-friendly ticket."""
        width = 40
        lines = []
        lines.append("=" * width)
        lines.append("KITCHEN ORDER".center(width))
        lines.append("=" * width)
        lines.append(f"Order #: {order_data.get('order_number', 'N/A')}")
        lines.append(f"Type:    {order_data.get('order_type', 'N/A')}")
        lines.append(f"Time:    {datetime.now().strftime('%H:%M:%S')}")
        lines.append("-" * width)

        for item in order_data.get("items", []):
            name = item.get("item_name", item.get("name", "Unknown"))
            qty = item.get("quantity", 1)
            lines.append(f"  {qty}x  {name}")
            instructions = item.get("special_instructions", "")
            if instructions:
                lines.append(f"       ** {instructions}")

        lines.append("=" * width)
        return "\n".join(lines)

    # -- event handler -------------------------------------------------------
    def _on_order_created(self, data: Dict[str, Any]) -> None:
        """Auto-print kitchen ticket when an order is created."""
        ticket = data.get("kitchen_ticket", "")
        if not ticket and data:
            ticket = self.format_kitchen_ticket(data)
        if ticket:
            self.print_content(ticket)


# ---------------------------------------------------------------------------
# Concrete display implementations
# ---------------------------------------------------------------------------

class KitchenDisplaySystem(BaseDisplay):
    """
    Kitchen Display System (KDS) for showing upcoming orders.

    Maintains an in-memory list of active orders and updates whenever
    order events fire.  In production the ``update_content`` method
    would push data to a secondary screen or web socket.
    """

    def __init__(self, display_name: str = "Kitchen Display"):
        super().__init__(display_name)
        self.active_orders: List[Dict[str, Any]] = []
        self._event_bus = EventBus.get_instance()
        self._event_bus.subscribe("order_created", self._on_order_created)
        self._event_bus.subscribe("order_status_changed", self._on_status_changed)
        self._event_bus.subscribe("order_completed", self._on_order_finished)
        self._event_bus.subscribe("order_cancelled", self._on_order_finished)

    def connect(self) -> bool:
        self.is_connected = True
        logger.info("KitchenDisplaySystem connected")
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("KitchenDisplaySystem disconnected")

    def update_content(self, content: Dict[str, Any]) -> bool:
        if not self.is_connected:
            return False
        # In production, push to display hardware / websocket
        logger.info("Kitchen display updated: %s", content.get("action"))
        return True

    def get_active_orders(self) -> List[Dict[str, Any]]:
        """Return the current list of active orders for the kitchen."""
        return list(self.active_orders)

    # -- event handlers -------------------------------------------------------
    def _on_order_created(self, data: Dict[str, Any]) -> None:
        order_entry = {
            "order_id": data.get("order_id"),
            "order_number": data.get("order_number"),
            "order_type": data.get("order_type"),
            "items": data.get("items", []),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
        }
        self.active_orders.append(order_entry)
        self.update_content({"action": "order_added", "order": order_entry})

    def _on_status_changed(self, data: Dict[str, Any]) -> None:
        order_id = data.get("order_id")
        new_status = data.get("new_status")
        for order in self.active_orders:
            if order.get("order_id") == order_id:
                order["status"] = new_status
                break
        self.update_content({"action": "status_changed", "order_id": order_id, "new_status": new_status})

    def _on_order_finished(self, data: Dict[str, Any]) -> None:
        order_id = data.get("order_id")
        self.active_orders = [o for o in self.active_orders if o.get("order_id") != order_id]
        self.update_content({"action": "order_removed", "order_id": order_id})


class CustomerDisplay(BaseDisplay):
    """
    Customer-facing display showing current order status.

    In production, this drives a secondary monitor or tablet showing
    order progress to the customer.
    """

    def __init__(self, display_name: str = "Customer Display"):
        super().__init__(display_name)
        self.current_content: Dict[str, Any] = {}
        self._event_bus = EventBus.get_instance()
        self._event_bus.subscribe("order_status_changed", self._on_status_changed)
        self._event_bus.subscribe("order_completed", self._on_order_completed)

    def connect(self) -> bool:
        self.is_connected = True
        logger.info("CustomerDisplay connected")
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("CustomerDisplay disconnected")

    def update_content(self, content: Dict[str, Any]) -> bool:
        if not self.is_connected:
            return False
        self.current_content = content
        logger.info("Customer display updated: %s", content.get("message", ""))
        return True

    # -- event handlers -------------------------------------------------------
    def _on_status_changed(self, data: Dict[str, Any]) -> None:
        status = data.get("new_status", "")
        order_number = data.get("order_number", "")
        messages = {
            "pending": f"Order {order_number} received",
            "preparing": f"Order {order_number} is being prepared",
            "ready": f"Order {order_number} is ready for pickup!",
        }
        self.update_content({
            "order_number": order_number,
            "status": status,
            "message": messages.get(status, f"Order {order_number}: {status}"),
        })

    def _on_order_completed(self, data: Dict[str, Any]) -> None:
        order_number = data.get("order_number", "")
        self.update_content({
            "order_number": order_number,
            "status": "completed",
            "message": f"Order {order_number} complete. Thank you!",
        })


# ---------------------------------------------------------------------------
# Hardware manager (registry)
# ---------------------------------------------------------------------------

class HardwareManager:
    """
    Central registry for all hardware peripherals.

    Provides ``connect_all`` / ``disconnect_all`` lifecycle methods and
    acts as a single access point for the rest of the application.
    """

    def __init__(self):
        self.receipt_printer: Optional[ReceiptPrinter] = None
        self.kitchen_printer: Optional[KitchenPrinter] = None
        self.kitchen_display: Optional[KitchenDisplaySystem] = None
        self.customer_display: Optional[CustomerDisplay] = None

    def initialize(
        self,
        receipt_printer_name: str = "",
        kitchen_printer_name: str = "",
        output_dir: str = "receipts",
    ) -> None:
        """Create and register all hardware components."""
        self.receipt_printer = ReceiptPrinter(receipt_printer_name, output_dir)
        self.kitchen_printer = KitchenPrinter(kitchen_printer_name, output_dir)
        self.kitchen_display = KitchenDisplaySystem()
        self.customer_display = CustomerDisplay()

    def connect_all(self) -> Dict[str, bool]:
        """Connect every registered peripheral and return a status map."""
        results: Dict[str, bool] = {}
        for name, device in self._devices():
            try:
                results[name] = device.connect()
            except Exception as exc:
                logger.error("Failed to connect %s: %s", name, exc)
                results[name] = False
        return results

    def disconnect_all(self) -> None:
        """Disconnect every registered peripheral."""
        for name, device in self._devices():
            try:
                device.disconnect()
            except Exception as exc:
                logger.error("Failed to disconnect %s: %s", name, exc)

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Return status of all registered peripherals."""
        return {name: device.get_status() for name, device in self._devices()}

    # -- internals -----------------------------------------------------------
    def _devices(self):
        """Yield (name, device) tuples for all non-None peripherals."""
        mapping = {
            "receipt_printer": self.receipt_printer,
            "kitchen_printer": self.kitchen_printer,
            "kitchen_display": self.kitchen_display,
            "customer_display": self.customer_display,
        }
        for name, device in mapping.items():
            if device is not None:
                yield name, device
