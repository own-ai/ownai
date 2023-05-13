"""Test the handling of AI chains."""
from flask import session

from backaind.brain import get_chain, reply


def test_get_chain_returns_from_session(client):
    """Test if the chain is loaded from session."""
    with client:
        client.get("/")
        session["chain[1]"] = "NotARealChain"
        session["chain_input_keys[1]"] = set("text_input")
        (chain, chain_input_keys) = get_chain(1)
        assert chain == "NotARealChain"
        assert chain_input_keys == set("text_input")


def test_get_chain_creates_new_chain_if_not_in_session(client, monkeypatch):
    """Test if the chain gets created if it doesn't exist yet."""
    with client:
        client.get("/")
        session["chain[1]"] = None
        monkeypatch.setattr(
            "backaind.brain.get_aifile_from_db",
            lambda _ai_id: {
                "input_keys": '["input_text"]',
                "chain": '{"name": "NotARealChain"}',
            },
        )
        monkeypatch.setattr(
            "backaind.brain.load_chain_from_config", lambda chain: chain
        )
        (chain, _chain_input_keys) = get_chain(1)
        assert chain == {"name": "NotARealChain"}
        assert session["chain[1]"] == {"name": "NotARealChain"}


def test_reply_runs_the_chain(monkeypatch):
    """Test if the reply function calls the chain."""

    class FakeChain:
        """Helper class to allow calling the chain."""

        def __call__(self, _inputs):
            """Mock function for calling the chain."""
            return {"output_text": "Response"}

    def fake_get_chain(_ai_id):
        return (FakeChain(), set())

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    response = reply(1, "Hi", None)

    assert response == "Response"


def test_reply_sets_inputs(monkeypatch):
    """Test if the reply function correctly sets the inputs for the chain."""

    class FakeChain:
        """Helper class to allow calling the chain."""

        def __call__(self, inputs):
            """Mock function for calling the chain."""
            output = (
                f"text={inputs['input_text']}, knowledge={inputs['input_knowledge']}"
            )
            return {"output_text": output}

    def fake_get_chain(_ai_id):
        return (FakeChain(), {"input_text", "input_knowledge", "input_unknown"})

    class FakeKnowledge:
        """Helper class for a fake knowledge interface."""

        def similarity_search(self, input_text):
            """Mock function to check if the similarity_search is called."""
            return [input_text]

    def fake_get_knowledge(_knowledge_id):
        return FakeKnowledge()

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    monkeypatch.setattr("backaind.brain.get_knowledge", fake_get_knowledge)

    response = reply(1, "Hi", 1)
    assert response == "text=Hi, knowledge=['Hi']"

    response = reply(1, "Hi", None)
    assert response == "text=Hi, knowledge=[]"
