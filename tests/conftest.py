"""Define test configuration and fixtures."""
import os
import shutil
import tempfile

import pytest
from backaind import create_app
from backaind.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), "data.sql"), "rb") as f:
    _data_sql = f.read().decode("utf8")


@pytest.fixture(name="app")
def fixture_app():
    """Factory function for the Flask server app fixture."""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            "TESTING": True,
            "DATABASE": db_path,
            "SECRET_KEY": "Only4Testing",
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)
    if os.path.exists("instance/test-knowledge-1"):
        shutil.rmtree("instance/test-knowledge-1")


@pytest.fixture(name="client")
def fixture_client(app):
    """Factory function for the test client fixture."""
    return app.test_client()


@pytest.fixture(name="runner")
def fixture_runner(app):
    """Factory function for the click CLI runner."""
    return app.test_cli_runner()


class AuthActions:
    """Helper class for authentication actions in tests."""

    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        """Perform a login."""
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        """Perform a logout."""
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    """Factory function for authentication actions."""
    return AuthActions(client)
