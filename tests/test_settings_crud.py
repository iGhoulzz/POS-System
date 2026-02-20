"""
Unit tests for Settings CRUD operations via SettingsManager.
"""

import pytest
from logic.settings_manager import SettingsManager


class TestSettingCreate:
    def test_create_new_setting(self):
        result = SettingsManager.set_setting("test_key", "test_value", "A test setting")
        assert result is True

    def test_default_settings_exist(self):
        assert SettingsManager.get_setting("tax_rate") is not None
        assert SettingsManager.get_setting("receipt_header") is not None
        assert SettingsManager.get_setting("receipt_footer") is not None


class TestSettingRead:
    def test_read_existing_setting(self):
        value = SettingsManager.get_setting("tax_rate")
        assert value == "0.08"

    def test_read_nonexistent_setting(self):
        assert SettingsManager.get_setting("nonexistent_key") is None

    def test_get_all_settings(self):
        settings = SettingsManager.get_all_settings()
        assert isinstance(settings, list)
        assert len(settings) >= 3  # at least the defaults

    def test_get_tax_rate(self):
        rate = SettingsManager.get_tax_rate()
        assert isinstance(rate, float)
        assert rate == 0.08


class TestSettingUpdate:
    def test_update_existing_setting(self):
        SettingsManager.set_setting("tax_rate", "0.10")
        assert SettingsManager.get_setting("tax_rate") == "0.10"

    def test_set_tax_rate(self):
        SettingsManager.set_tax_rate(0.05)
        assert SettingsManager.get_tax_rate() == 0.05

    def test_set_receipt_header(self):
        SettingsManager.set_receipt_header("My Shop")
        assert SettingsManager.get_receipt_header() == "My Shop"


class TestSettingDelete:
    def test_delete_setting(self):
        SettingsManager.set_setting("temp_key", "temp_val")
        assert SettingsManager.delete_setting("temp_key") is True
        assert SettingsManager.get_setting("temp_key") is None


class TestPrinterSettings:
    def test_get_printer_settings_defaults(self):
        ps = SettingsManager.get_printer_settings()
        assert "receipt_printer" in ps
        assert "kitchen_printer" in ps

    def test_set_printer_settings(self):
        SettingsManager.set_printer_settings(
            receipt_printer="POS-Printer-1",
            kitchen_printer="Kitchen-Printer-1",
            auto_print_receipt=True,
            auto_print_kitchen=True,
        )
        ps = SettingsManager.get_printer_settings()
        assert ps["receipt_printer"] == "POS-Printer-1"
        assert ps["kitchen_printer"] == "Kitchen-Printer-1"
        assert ps["auto_print_receipt"] == "true"
        assert ps["auto_print_kitchen"] == "true"


class TestCompanyInfo:
    def test_set_and_get_company_info(self):
        SettingsManager.set_company_info(
            name="Test Corp", address="123 Test St", phone="555-0000"
        )
        info = SettingsManager.get_company_info()
        assert info["name"] == "Test Corp"
        assert info["address"] == "123 Test St"
        assert info["phone"] == "555-0000"
