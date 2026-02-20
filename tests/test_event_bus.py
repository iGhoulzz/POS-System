"""
Unit tests for the EventBus – the backbone of cross-component communication.
"""

import pytest
from logic.event_bus import EventBus


class TestEventBusSingleton:
    def test_get_instance_returns_same_object(self):
        a = EventBus.get_instance()
        b = EventBus.get_instance()
        assert a is b

    def test_reset_instance_creates_new(self):
        old = EventBus.get_instance()
        EventBus.reset_instance()
        new = EventBus.get_instance()
        assert old is not new


class TestSubscribePublish:
    def test_subscriber_receives_event(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe("test_event", lambda d: received.append(d))
        bus.publish("test_event", {"key": "value"})
        assert len(received) == 1
        assert received[0]["key"] == "value"

    def test_multiple_subscribers(self):
        bus = EventBus.get_instance()
        results = {"a": [], "b": []}
        bus.subscribe("multi", lambda d: results["a"].append(d))
        bus.subscribe("multi", lambda d: results["b"].append(d))
        bus.publish("multi", {"x": 1})
        assert len(results["a"]) == 1
        assert len(results["b"]) == 1

    def test_publish_without_data(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe("no_data", lambda d: received.append(d))
        bus.publish("no_data")
        assert received == [{}]

    def test_publish_to_nonexistent_event(self):
        bus = EventBus.get_instance()
        # Should not raise
        bus.publish("does_not_exist", {"data": True})


class TestUnsubscribe:
    def test_unsubscribe_stops_notifications(self):
        bus = EventBus.get_instance()
        received = []
        handler = lambda d: received.append(d)
        bus.subscribe("unsub_test", handler)
        bus.publish("unsub_test", {})
        assert len(received) == 1
        bus.unsubscribe("unsub_test", handler)
        bus.publish("unsub_test", {})
        assert len(received) == 1  # should not have increased

    def test_unsubscribe_nonexistent_handler(self):
        bus = EventBus.get_instance()
        # Should not raise
        bus.unsubscribe("anything", lambda d: None)


class TestClear:
    def test_clear_removes_all_subscribers(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe("clear_test", lambda d: received.append(d))
        bus.clear()
        bus.publish("clear_test", {})
        assert len(received) == 0


class TestErrorHandling:
    def test_failing_handler_does_not_break_others(self):
        bus = EventBus.get_instance()
        received = []

        def bad_handler(d):
            raise RuntimeError("boom")

        bus.subscribe("err", bad_handler)
        bus.subscribe("err", lambda d: received.append(d))
        bus.publish("err", {"ok": True})
        # The second handler should still have been called
        assert len(received) == 1


class TestOrderEvents:
    """Simulate order events flowing through the bus."""

    def test_order_created_event(self):
        bus = EventBus.get_instance()
        received = []
        bus.subscribe("order_created", lambda d: received.append(d))
        bus.publish("order_created", {
            "order_id": 1,
            "order_number": "ORD-001",
            "items": [{"name": "Latte", "quantity": 2}],
        })
        assert received[0]["order_id"] == 1

    def test_order_status_changed_event(self):
        bus = EventBus.get_instance()
        statuses = []
        bus.subscribe("order_status_changed", lambda d: statuses.append(d["new_status"]))

        for status in ("preparing", "ready", "completed"):
            bus.publish("order_status_changed", {
                "order_id": 1,
                "new_status": status,
            })
        assert statuses == ["preparing", "ready", "completed"]
