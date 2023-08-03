"""Test the handling of AI chains."""
import os
import pytest
from langchain.chains.loading import load_chain_from_config
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferWindowMemory
from backaind.aifile import read_aifile_from_path
from backaind.brain import (
    get_chain,
    reply,
    reset_global_chain,
    find_instances,
    set_text_generation_inference_token,
    UpdatedEnvironment,
)
import backaind.brain


def test_get_chain_loads_from_global_chain():
    """Test if the chain is loaded from the global chain instance."""
    backaind.brain.global_chain = "NotARealChain"
    backaind.brain.global_chain_id = 1
    backaind.brain.global_chain_input_keys = set("text_input")
    (chain, chain_input_keys) = get_chain(1)
    assert chain == "NotARealChain"
    assert chain_input_keys == set("text_input")
    reset_global_chain()


def test_get_chain_creates_new_chain(monkeypatch):
    """Test if the chain gets created if it doesn't exist yet."""
    reset_global_chain()
    monkeypatch.setattr(
        "backaind.brain.get_aifile_from_db",
        lambda _ai_id: {
            "input_keys": '["input_text"]',
            "chain": '{"name": "NotARealChain"}',
        },
    )
    monkeypatch.setattr("backaind.brain.load_chain_from_config", lambda chain: chain)
    (chain, _chain_input_keys) = get_chain(1)
    assert chain == {"name": "NotARealChain"}
    assert backaind.brain.global_chain == {"name": "NotARealChain"}
    reset_global_chain()


def test_reply_runs_the_chain(monkeypatch):
    """Test if the reply function calls the chain."""

    class FakeChain:
        """Helper class to allow calling the chain."""

        def __call__(self, _inputs, **_kwargs):
            """Mock function for calling the chain."""
            return {"output_text": "Response"}

    def fake_get_chain(_ai_id, _updated_environment):
        return (FakeChain(), set())

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    response = reply(1, "Hi", None)

    assert response == "Response"


def test_reply_sets_inputs(monkeypatch):
    """Test if the reply function correctly sets the inputs for the chain."""

    class FakeChain:
        """Helper class to allow calling the chain."""

        def __call__(self, inputs, **_kwargs):
            """Mock function for calling the chain."""
            output = f"{inputs['input_text']},{inputs['input_knowledge']},{inputs['input_history']}"
            return {"output_text": output}

    def fake_get_chain(_ai_id, _updated_environment):
        return (
            FakeChain(),
            {"input_text", "input_knowledge", "input_history", "input_unknown"},
        )

    class FakeKnowledge:
        """Helper class for a fake knowledge interface."""

        def similarity_search(self, input_text, **_kwargs):
            """Mock function to check if the similarity_search is called."""
            return [input_text]

    def fake_get_knowledge(_knowledge_id):
        return FakeKnowledge()

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    monkeypatch.setattr("backaind.brain.get_knowledge", fake_get_knowledge)

    response = reply(1, "Hi", 1)
    assert response == "Hi,['Hi'],"

    response = reply(1, "Hi", None)
    assert response == "Hi,[],"

    memory = ConversationBufferWindowMemory(k=3)
    memory.chat_memory.add_ai_message("Hi user")
    memory.chat_memory.add_user_message("Hi AI")
    response = reply(1, "Hi", 1, memory)
    assert response == "Hi,['Hi'],AI: Hi user\nHuman: Hi AI"


def test_set_text_generation_inference_token():
    """Test if the text generation inference token is set correctly."""
    aifile = read_aifile_from_path(
        "examples/huggingface_textgen_inference/huggingface_textgen_inference.aifile"
    )
    chain = load_chain_from_config(aifile["chain"])
    os.environ["TEXT_GENERATION_INFERENCE_TOKEN"] = "test_token"
    set_text_generation_inference_token(chain)
    all_huggingface_instances = find_instances(chain, HuggingFaceTextGenInference)
    assert len(all_huggingface_instances) == 1
    assert all_huggingface_instances[0].client.headers == {
        "Authorization": "Bearer test_token"
    }


def test_updated_environment_resets_values():
    """Test if the environment is reset after the context manager."""
    os.environ["EXISTING_VAR"] = "old_value"
    if "NEW_VAR" in os.environ:
        del os.environ["NEW_VAR"]

    with UpdatedEnvironment({"NEW_VAR": "new_value", "EXISTING_VAR": "new_value"}):
        assert os.getenv("NEW_VAR") == "new_value"
        assert os.getenv("EXISTING_VAR") == "new_value"

    assert os.getenv("NEW_VAR") is None
    assert os.getenv("EXISTING_VAR") == "old_value"


def test_updated_environment_handles_exceptions():
    """Test if the environment is reset even if an exception is raised."""
    os.environ["EXISTING_VAR"] = "old_value"
    if "NEW_VAR" in os.environ:
        del os.environ["NEW_VAR"]

    with pytest.raises(RuntimeError):
        with UpdatedEnvironment({"NEW_VAR": "new_value", "EXISTING_VAR": "new_value"}):
            assert os.getenv("NEW_VAR") == "new_value"
            assert os.getenv("EXISTING_VAR") == "new_value"
            raise RuntimeError("Test")

    assert os.getenv("NEW_VAR") is None
    assert os.getenv("EXISTING_VAR") == "old_value"
