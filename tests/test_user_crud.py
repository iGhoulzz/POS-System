"""
Unit tests for User CRUD operations via UserManager.
"""

import pytest
from logic.user_manager import UserManager


class TestUserCreate:
    def test_create_user_success(self):
        result = UserManager.create_user("cashier1", "pass123", "cashier", "Jane Doe")
        assert result is True

    def test_create_user_duplicate_username(self):
        UserManager.create_user("dup_user", "pass", "cashier", "Dup")
        result = UserManager.create_user("dup_user", "pass", "cashier", "Dup2")
        assert result is False

    def test_create_user_all_roles(self):
        for role in ("admin", "cashier", "kitchen"):
            assert UserManager.create_user(
                f"user_{role}", "pw", role, f"Test {role}"
            ) is True


class TestUserRead:
    def test_get_all_users_includes_default_admin(self):
        users = UserManager.get_all_users()
        assert any(u["username"] == "admin" for u in users)

    def test_get_user_by_id(self, admin_user_id):
        user = UserManager.get_user_by_id(admin_user_id)
        assert user is not None
        assert user["username"] == "admin"
        assert user["role"] == "admin"

    def test_get_user_by_invalid_id(self):
        assert UserManager.get_user_by_id(99999) is None


class TestUserUpdate:
    def test_update_full_name(self, admin_user_id):
        result = UserManager.update_user(admin_user_id, full_name="New Name")
        assert result is True
        user = UserManager.get_user_by_id(admin_user_id)
        assert user["full_name"] == "New Name"

    def test_update_role(self, admin_user_id):
        result = UserManager.update_user(admin_user_id, role="cashier")
        assert result is True
        user = UserManager.get_user_by_id(admin_user_id)
        assert user["role"] == "cashier"

    def test_update_no_fields_returns_false(self, admin_user_id):
        assert UserManager.update_user(admin_user_id) is False


class TestUserDelete:
    def test_soft_delete_deactivates(self, admin_user_id):
        result = UserManager.delete_user(admin_user_id)
        assert result is True
        user = UserManager.get_user_by_id(admin_user_id)
        assert user["is_active"] == 0


class TestUserAuthentication:
    def test_authenticate_valid_credentials(self):
        user = UserManager.authenticate_user("admin", "admin123")
        assert user is not None
        assert user["username"] == "admin"

    def test_authenticate_wrong_password(self):
        assert UserManager.authenticate_user("admin", "wrong") is None

    def test_authenticate_nonexistent_user(self):
        assert UserManager.authenticate_user("ghost", "pass") is None

    def test_authenticate_deactivated_user(self, admin_user_id):
        UserManager.delete_user(admin_user_id)  # soft delete
        assert UserManager.authenticate_user("admin", "admin123") is None
