"""Test the Flask server app factory."""
from backaind import create_app


def test_config():
    """Test whether the app factory takes an external test configuration."""
    assert not create_app().testing
    assert create_app({"TESTING": True}).testing
