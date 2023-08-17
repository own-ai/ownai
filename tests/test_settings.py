"""Test the settings blueprint."""
import os
import pytest
from flask import session
from backaind.auth import is_password_correct, set_password
from backaind.settings import EXTERNAL_PROVIDER_ENVVARS, get_settings

SETTINGS_PATHS = (
    "/settings/password",
    "/settings/external-providers",
)


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


def test_password_change_fails_for_demo_user(client):
    """Test whether the password does not get changed for the demo user."""
    with client:
        os.environ["ENABLE_DEMO_MODE"] = "1"
        response = client.post(
            "/settings/password",
            data={
                "current-password": "test",
                "new-password": "a" * 10,
                "new-password-confirmation": "a" * 10,
            },
        )
        assert b"You cannot change the password of the demo user." in response.data
        assert not is_password_correct("test", "a" * 10)
        assert not is_password_correct("demo", "a" * 10)
        del os.environ["ENABLE_DEMO_MODE"]


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


def test_get_external_providers_page(client, auth):
    """Test whether the external providers page gets displayed."""
    auth.login()
    response = client.get("/settings/external-providers")
    assert b"<h3>Connect to external AI providers</h3>" in response.data


def test_save_external_providers_fails_for_demo_user(client):
    """Test whether external providers do not get saved for the demo user."""
    with client:
        os.environ["ENABLE_DEMO_MODE"] = "1"
        response = client.post(
            "/settings/external-providers",
            data={
                EXTERNAL_PROVIDER_ENVVARS[0]: "test",
            },
        )
        assert (
            b"You cannot change the external providers settings of the demo user."
            in response.data
        )
        assert get_settings(-1).get("external-providers", {}) == {}
        del os.environ["ENABLE_DEMO_MODE"]


def test_save_external_providers(auth, client):
    """Test whether external providers get inserted, updated and deleted correctly."""
    with client:
        auth.login()
        user_id = session["user_id"]
        provider1 = EXTERNAL_PROVIDER_ENVVARS[0]
        provider2 = EXTERNAL_PROVIDER_ENVVARS[1]
        assert get_settings(user_id).get("external-providers", {}) == {}

        response = client.post(
            "/settings/external-providers",
            data={
                provider1: "test1",
                provider2: "test2",
            },
        )
        assert b"Settings saved successfully." in response.data
        assert (
            get_settings(user_id).get("external-providers", {}).get(provider1)
            == "test1"
        )
        assert (
            get_settings(user_id).get("external-providers", {}).get(provider2)
            == "test2"
        )

        response = client.post(
            "/settings/external-providers",
            data={
                provider2: "test2_new",
            },
        )
        assert b"Settings saved successfully." in response.data
        assert (
            get_settings(user_id).get("external-providers", {}).get(provider1) is None
        )
        assert (
            get_settings(user_id).get("external-providers", {}).get(provider2)
            == "test2_new"
        )

        response = client.post(
            "/settings/external-providers",
            data={},
        )
        assert b"Settings saved successfully." in response.data
        assert get_settings(user_id).get("external-providers", {}) == {}
