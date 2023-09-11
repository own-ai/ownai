"""Test the Flask server app factory."""
import os
from backaind import create_app


def test_config():
    """Test whether the app factory takes an external test configuration."""
    os.environ["OWNAI_SQLALCHEMY_DATABASE_URI"] = "sqlite:///testing.db"
    assert not create_app().testing
    assert create_app(
        {"SQLALCHEMY_DATABASE_URI": "sqlite:///testing.db", "TESTING": True}
    ).testing
