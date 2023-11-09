"""Test the AI API."""
import json
import pytest
from backaind.extensions import db
from backaind.models import Ai


def test_auth_required(client):
    """Test whether authorization is required to access the API."""
    assert client.get("/api/ai/").status_code == 401
    assert client.get("/api/ai/2").status_code == 401
    assert client.post("/api/ai/", json={}).status_code == 401
    assert client.put("/api/ai/1", json={}).status_code == 401
    assert client.delete("/api/ai/1").status_code == 401


def test_get_all_ais(client, auth):
    """Test if GET /api/ai/ returns all AIs from the database."""
    auth.login()
    response = client.get("/api/ai/")
    assert 2 == len(json.loads(response.data))


def test_get_ai(client, auth):
    """Test if GET /api/ai/1 returns the AI with id 1."""
    auth.login()
    response = client.get("/api/ai/1")
    assert 1 == json.loads(response.data)["id"]


def test_get_unknown_ai_returns_404(client, auth):
    """Test if GET /api/ai/999 returns 404."""
    auth.login()
    response = client.get("/api/ai/999")
    assert response.status_code == 404


def test_create_ai(client, auth, app):
    """Test if POST /api/ai/ creates a new AI."""
    auth.login()
    response = client.post(
        "/api/ai/", json={"name": "Test", "input_keys": ["input_text"], "chain": {}}
    )
    assert json.loads(response.data)["id"] == 3
    with app.app_context():
        entry = db.get_or_404(Ai, 3)
        assert entry and entry.name == "Test"


def test_update_ai(client, auth, app):
    """Test if PUT /api/ai/1 updates the AI."""
    auth.login()
    response = client.put(
        "/api/ai/1", json={"name": "Test", "input_keys": ["input_text"], "chain": {}}
    )
    assert json.loads(response.data)["name"] == "Test"
    with app.app_context():
        entry = db.get_or_404(Ai, 1)
        assert entry and entry.name == "Test"


def test_delete_ai(client, auth, app):
    """Test if DELETE /api/ai/1 deletes the AI."""
    auth.login()
    response = client.delete("/api/ai/1")
    assert response.status_code == 204
    with app.app_context():
        entry = db.session.get(Ai, 1)
        assert entry is None


@pytest.mark.parametrize(
    "data,message",
    (
        (
            {},
            "The AI file cannot be empty.",
        ),
        (
            {"input_keys": [], "chain": {}},
            'The property "name" is required.',
        ),
        (
            {"name": 1, "input_keys": [], "chain": {}},
            'The property "name" has to be a string.',
        ),
        (
            {"name": "Test", "chain": {}},
            'The property "input_keys" is required.',
        ),
        (
            {"name": "Test", "input_keys": "input_text", "chain": {}},
            'The property "input_keys" has to be a list of strings.',
        ),
        (
            {"name": "Test", "input_keys": []},
            'The property "chain" is required.',
        ),
        (
            {"name": "Test", "input_keys": [], "chain": []},
            'The property "chain" has to be a chain object.',
        ),
        (
            {"name": "Test", "input_keys": [], "chain": {}, "input_labels": "Test"},
            'The property "input_labels" has to be an object assigning input keys to labels.',
        ),
        (
            {"name": "Test", "input_keys": [], "chain": {}, "greeting": True},
            'The property "greeting" has to be a string.',
        ),
    ),
)
def test_validation(client, auth, data, message):
    """Test if the AI JSON validation works."""
    auth.login()
    for response in (
        client.post("/api/ai/", json=data),
        client.put("/api/ai/1", json=data),
    ):
        assert response.status_code == 400
        assert json.loads(response.data)["error"] == message
