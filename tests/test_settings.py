"""Test the settings blueprint."""
import pytest
from backaind.auth import is_password_correct, set_password

SETTINGS_PATHS = ("/settings/password",)


@pytest.mark.parametrize("path", SETTINGS_PATHS)
def test_login_required(client, path):
    """Test whether login is required to view all settings paths."""
    response = client.get(path)
    assert response.headers["Location"] == "/auth/login"


def test_get_password_change_page(client, auth):
    """Test whether the password change page gets displayed."""
    auth.login()
    response = client.get("/settings/password")
    assert b"Change Password" in response.data


def test_password_change_fails_on_incorrect_current_password(auth, app, client):
    """Test whether the password does not get changed when the current password is incorrect."""
    with app.app_context():
        auth.login()
        assert is_password_correct("test", "test")
        response = client.post(
            "/settings/password",
            data={
                "current-password": "a",
                "new-password": "test",
                "new-password-confirmation": "test",
            },
        )
        assert b"Incorrect current password." in response.data
        assert not is_password_correct("test", "a")
        assert is_password_correct("test", "test")


def test_password_change_fails_on_non_matching_passwords(auth, app, client):
    """
    Test whether the password does not get changed when the password and
    the password confirmation do not match.
    """
    with app.app_context():
        auth.login()
        assert is_password_correct("test", "test")
        response = client.post(
            "/settings/password",
            data={
                "current-password": "test",
                "new-password": "a",
                "new-password-confirmation": "b",
            },
        )
        assert b"Password and confirmation do not match." in response.data
        assert not is_password_correct("test", "a")
        assert is_password_correct("test", "test")


def test_password_change_fails_on_too_short_password(auth, app, client):
    """Test whether the password does not get changed when the new password is too short."""
    with app.app_context():
        auth.login()
        assert is_password_correct("test", "test")
        response = client.post(
            "/settings/password",
            data={
                "current-password": "test",
                "new-password": "a",
                "new-password-confirmation": "a",
            },
        )
        assert b"Password must be at least 10 characters long." in response.data
        assert not is_password_correct("test", "a")
        assert is_password_correct("test", "test")


def test_password_change_works(auth, app, client):
    """Test whether the password change works."""
    with app.app_context():
        auth.login()
        assert is_password_correct("test", "test")
        response = client.post(
            "/settings/password",
            data={
                "current-password": "test",
                "new-password": "a" * 10,
                "new-password-confirmation": "a" * 10,
            },
        )
        assert b"Password changed successfully." in response.data
        assert not is_password_correct("test", "test")
        assert is_password_correct("test", "a" * 10)
        set_password("test", "test")
        assert not is_password_correct("test", "a" * 10)
        assert is_password_correct("test", "test")
