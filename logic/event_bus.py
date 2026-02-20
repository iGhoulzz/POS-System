"""
Event bus for real-time cross-component communication.

Enables decoupled communication between POS screens, kitchen displays,
printers, and other hardware/software components. When an order status
changes, all registered listeners are notified automatically.

Supported events:
    - order_created: New order placed (triggers kitchen display + kitchen printer)
    - order_status_changed: Order status updated (triggers display refresh)
    - order_completed: Order finished (triggers receipt printer)
    - order_cancelled: Order cancelled (triggers display refresh)
    - menu_item_updated: Menu item changed (triggers kiosk/POS refresh)
    - user_logged_in: User authentication event
    - user_logged_out: User logout event
"""

import threading
import logging
from typing import Callable, Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class EventBus:
    """
    Thread-safe singleton event bus for system-wide event communication.

    Usage:
        bus = EventBus.get_instance()
        bus.subscribe("order_created", my_handler)
        bus.publish("order_created", {"order_id": 1, "order_number": "ORD-001"})
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._sub_lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> "EventBus":
        """Get or create the singleton EventBus instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (used for testing)."""
        with cls._lock:
            cls._instance = None

    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Event name to listen for.
            callback: Function to call when the event fires.
                      Signature: callback(event_data: dict) -> None
        """
        with self._sub_lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                logger.debug("Subscriber added for event: %s", event_type)

    def unsubscribe(self, event_type: str, callback: Callable) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Event name to stop listening for.
            callback: The previously registered callback to remove.
        """
        with self._sub_lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                    logger.debug("Subscriber removed for event: %s", event_type)
                except ValueError:
                    pass

    def publish(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event_type: Event name to fire.
            data: Optional dictionary of event data.
        """
        with self._sub_lock:
            subscribers = list(self._subscribers.get(event_type, []))

        for callback in subscribers:
            try:
                callback(data or {})
            except Exception as e:
                logger.error(
                    "Error in event handler for '%s': %s", event_type, e
                )

    def clear(self) -> None:
        """Remove all subscribers (used for testing)."""
        with self._sub_lock:
            self._subscribers.clear()
