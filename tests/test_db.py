"""Test the database connection module."""
import sqlite3

import pytest
from backaind.db import get_db


def test_get_close_db(app):
    """Test whether the database connection gets closed when the app context is terminated."""
    with app.app_context():
        database = get_db()
        assert database is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as error:
        database.execute("SELECT 1")

    assert "closed" in str(error.value)


def test_init_db_command(runner, monkeypatch):
    """Test whether the init-db command works."""

    class Recorder:
        """Helper class to record function call."""

        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr("backaind.db.init_db", fake_init_db)
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert Recorder.called
