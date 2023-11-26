"""Test the Ainteraction module to interact with AI applications."""
import pytest

from backaind.ainteraction import (
    handle_incoming_message,
    get_ai_data,
    get_knowledge_data,
    is_ai_public,
    is_knowledge_public,
    send_progress,
    send_next_token,
    send_response,
)


def test_no_public_ai_redirects_to_login(client, monkeypatch):
    """Test whether the ainteraction page redirects to the login page if no public AI exists."""
    monkeypatch.setattr(
        "backaind.ainteraction.get_ai_data",
        lambda only_public: [] if only_public else ["error"],
    )
    response = client.get("/")
    assert response.headers["Location"] == "/auth/login"


def test_public_ai_shows_ainteraction_page(client, monkeypatch):
    """Test whether the ainteraction page loads if a public AI exists."""
    test_ai_data = [
        {
            "id": 123,
            "name": "Test AI",
            "input_keys": ["input_text"],
            "input_labels": {"input_text": "Input Text"},
            "greeting": "Hello!",
        }
    ]
    monkeypatch.setattr(
        "backaind.ainteraction.get_ai_data",
        lambda only_public: [test_ai_data] if only_public else ["error"],
    )
    response = client.get("/")
    assert b"Hello" in response.data
    assert b'id="ainteraction"' in response.data


@pytest.mark.parametrize("path", ("/",))
def test_index(client, auth, path):
    """Test whether the ainteraction page loads if the user is logged in."""
    auth.login()
    response = client.get(path)
    assert b"Hello" in response.data
    assert b'id="ainteraction"' in response.data


test_incoming_message = {
    "responseId": 1,
    "message": {
        "id": 2,
        "author": {
            "species": "human",
        },
        "date": "2023-04-15T23:53:04.745556",
        "text": "Fine and you?",
    },
    "history": [
        {
            "id": 0,
            "author": {
                "species": "human",
            },
            "date": "2023-04-15T23:53:04.745556",
            "text": "Hi!",
        },
        {
            "id": 1,
            "author": {
                "species": "ai",
            },
            "date": "2023-04-15T23:53:04.745556",
            "text": "Hi, how are you?",
        },
    ],
}


def test_handle_incoming_message_without_login_disconnects(client, monkeypatch):
    """
    Test whether the server disconnects on incoming socket.io messages without valid user
    context if the AI or knowledge is not public.
    """

    class DisconnectRecorder:
        """Helper class to record function call to disconnect()."""

        called = 0

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        called = 0

    def fake_disconnect():
        DisconnectRecorder.called += 1

    def fake_emit(_event, _arg):
        EmitRecorder.called += 1

    monkeypatch.setattr("backaind.ainteraction.disconnect", fake_disconnect)
    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)

    with client:
        client.get("/")

        # aiId is missing
        handle_incoming_message(test_incoming_message)

        # non-public AI
        test_incoming_message["aiId"] = 2
        handle_incoming_message(test_incoming_message)

        # public AI, but non-public knowledge
        test_incoming_message["aiId"] = 1
        test_incoming_message["knowledgeId"] = 2
        handle_incoming_message(test_incoming_message)
        del test_incoming_message["knowledgeId"]

    assert DisconnectRecorder.called == 3
    assert EmitRecorder.called == 0


def test_handle_incoming_message(client, auth, monkeypatch):
    """Test whether the server emits a response for incoming socket.io messages."""

    class DisconnectRecorder:
        """Helper class to record function call to disconnect()."""

        called = 0

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        called_for_token = 0
        called_for_message = 0

    def fake_disconnect():
        DisconnectRecorder.called += 1

    def fake_emit(event, _arg):
        if event == "token":
            EmitRecorder.called_for_token += 1
        elif event == "message":
            EmitRecorder.called_for_message += 1

    def fake_reply(
        _ai_id,
        _input_text,
        _knowledge_id,
        _memory,
        on_token,
        _on_progress,
        _updated_environment,
    ):
        on_token("token")
        return "Fake response"

    monkeypatch.setattr("backaind.ainteraction.disconnect", fake_disconnect)
    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)
    monkeypatch.setattr("backaind.ainteraction.reply", fake_reply)

    with client:
        client.get("/")

        # public AI
        test_incoming_message["aiId"] = 1
        handle_incoming_message(test_incoming_message)

        # non-public AI after login
        auth.login()
        test_incoming_message["aiId"] = 2
        handle_incoming_message(test_incoming_message)

    assert DisconnectRecorder.called == 0
    assert EmitRecorder.called_for_token == 2
    assert EmitRecorder.called_for_message == 2


def test_handle_incoming_message_sends_error_message(client, auth, monkeypatch):
    """Test whether exceptions during generation are returned as error message."""

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        text = None
        status = None

    def fake_emit(_event, _arg):
        EmitRecorder.text = _arg["text"]
        EmitRecorder.status = _arg["status"]

    def fake_reply(*_args):
        raise NotImplementedError("Test Exception")

    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)
    monkeypatch.setattr("backaind.ainteraction.reply", fake_reply)

    auth.login()
    with client, pytest.raises(NotImplementedError):
        client.get("/")
        test_incoming_message["aiId"] = 1
        handle_incoming_message(test_incoming_message)

    assert EmitRecorder.text == "Test Exception"
    assert EmitRecorder.status == "error"


def test_get_ai_data_returns_all_ais(app):
    """Test whether get_ai_data returns all AIs if only_public is false."""
    with app.app_context():
        assert len(get_ai_data(False)) == 2


def test_get_ai_data_returns_only_public(app):
    """Test whether get_ai_data returns only public AIs if only_public is true."""
    with app.app_context():
        assert len(get_ai_data(True)) == 1


def test_get_knowledge_data_returns_all_knowledge(app):
    """Test whether get_knowledge_data returns all knowledge if only_public is false."""
    with app.app_context():
        assert len(get_knowledge_data(False)) == 2


def test_get_knowledge_data_returns_only_public(app):
    """Test whether get_knowledge_data returns only public knowledge if only_public is true."""
    with app.app_context():
        assert len(get_knowledge_data(True)) == 1


def test_is_ai_public(app):
    """Test whether is_ai_public returns true only if the AI is public."""
    with app.app_context():
        assert is_ai_public(1)
        assert not is_ai_public(2)


def test_is_knowledge_public(app):
    """Test whether is_knowledge_public returns true only if the knowledge is public."""
    with app.app_context():
        assert is_knowledge_public(1)
        assert not is_knowledge_public(2)


def test_send_progress_emits_progress(monkeypatch):
    """Test if a call to send_progress emits the 'progress' event."""

    class EmitRecorder:
        """Helper class to record function call to emit()."""

        event = None

    def fake_emit(event, _arg):
        EmitRecorder.event = event

    monkeypatch.setattr("backaind.ainteraction.emit", fake_emit)
    send_progress(1, 100)

    assert EmitRecorder.event == "progress"


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
