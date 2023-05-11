"""Test the Ainteraction module to interact with AI applications."""
import pytest

from backaind.ainteraction import (
    handle_incoming_message,
    send_next_token,
    send_response,
)


@pytest.mark.parametrize("path", ("/",))
def test_login_required(client, path):
    """Test whether a login is required to view path."""
    response = client.get(path)
    assert response.headers["Location"] == "/auth/login"


def test_index(client, auth):
    """Test whether the ainteraction page gets displayed."""
    auth.login()
    response = client.get("/")
    assert b"Hello - ownAI" in response.data
    assert b'<div id="ainteraction">' in response.data


test_incoming_message = {
    "responseId": 1,
    "message": {
        "id": 0,
        "author": {
            "species": "human",
        },
        "date": "2023-04-15T23:53:04.745556",
        "text": "Hi, how are you?",
    },
}


def test_handle_incoming_message_without_login_disconnects(client, monkeypatch):
    """
    Test whether the server disconnects on incoming socket.io messages without valid user
    context.
    """

    class DisconnectRecorder:
        """Helper class to record function call to disconnect()."""

        called = False

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        called = False

    def fake_disconnect():
        DisconnectRecorder.called = True

    def fake_emit(_event, _arg):
        EmitRecorder.called = True

    monkeypatch.setattr("backaind.ainteraction.disconnect", fake_disconnect)
    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)

    with client:
        client.get("/")
        handle_incoming_message(test_incoming_message)

    assert DisconnectRecorder.called
    assert not EmitRecorder.called


def test_handle_incoming_message(client, auth, monkeypatch):
    """Test whether the server emits a response for incoming socket.io messages."""

    class DisconnectRecorder:
        """Helper class to record function call to disconnect()."""

        called = False

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        called = False

    def fake_disconnect():
        DisconnectRecorder.called = True

    def fake_emit(_event, _arg):
        EmitRecorder.called = True

    def fake_reply(_message):
        return "Fake response"

    monkeypatch.setattr("backaind.ainteraction.disconnect", fake_disconnect)
    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)
    monkeypatch.setattr("backaind.ainteraction.reply", fake_reply)

    auth.login()
    with client:
        client.get("/")
        handle_incoming_message(test_incoming_message)

    assert not DisconnectRecorder.called
    assert EmitRecorder.called


def test_send_next_token_emits_token(monkeypatch):
    """Test if a call to send_next_token emits the 'token' event."""

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        event = None

    def fake_emit(event, _arg):
        EmitRecorder.event = event

    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)
    send_next_token(1, "token_text")

    assert EmitRecorder.event == "token"


def test_send_response_emits_message(monkeypatch):
    """Test if a call to send_response emits the 'message' event."""

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        event = None

    def fake_emit(event, _arg):
        EmitRecorder.event = event

    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)
    send_response(1, "message_text")

    assert EmitRecorder.event == "message"
