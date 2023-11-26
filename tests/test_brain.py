"""Test the handling of AI chains."""
import os
import queue

from langchain.chains.loading import load_chain_from_config
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferWindowMemory
import pytest

from backaind.aifile import read_aifile_from_path
from backaind.brain import (
    find_instances,
    get_chain,
    reply,
    reset_global_chain,
    run_chain_on_gunicorn,
    run_chain_on_multiprocessing,
    run_chain_process,
    set_text_generation_inference_token,
    estimate_processing_time,
    UpdatedEnvironment,
)
import backaind.brain
from backaind.models import Ai


class FakeChain:
    """Helper class to mock a chain."""

    def __call__(self, inputs, **kwargs):
        """Mock function for calling the chain."""
        if kwargs.get("callbacks"):
            for callback_handler in kwargs["callbacks"]:
                callback_handler.on_chat_model_start(None, None)
                callback_handler.on_llm_start({}, ["testprompt"])
                callback_handler.on_llm_new_token("testtoken")
        output = f"{inputs['input_text']},{inputs['input_knowledge']},{inputs['input_history']}"
        return {"output_text": output}


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
        "backaind.extensions.db.get_or_404",
        lambda _model, _model_id: Ai(
            input_keys=["input_text"],
            chain={"name": "NotARealChain"},
        ),
    )
    monkeypatch.setattr("backaind.brain.load_chain_from_config", lambda chain: chain)
    (chain, _chain_input_keys) = get_chain(1)
    assert chain == {"name": "NotARealChain"}
    assert backaind.brain.global_chain == {"name": "NotARealChain"}
    reset_global_chain()


def test_reply_runs_the_chain(monkeypatch):
    """Test if the reply function runs the chain."""

    def fake_get_chain(_ai_id, _updated_environment):
        return (FakeChain(), set(("input_text", "input_knowledge", "input_history")))

    def fake_run(chain, inputs, _on_token, _on_progress):
        return chain(inputs)["output_text"]

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    monkeypatch.setattr("backaind.brain.run_chain_on_multiprocessing", fake_run)
    response = reply(1, "Hi", None)

    assert response == "Hi,[],"


def test_reply_sets_inputs(monkeypatch):
    """Test if the reply function correctly sets the inputs for the chain."""

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

    def fake_run(chain, inputs, _on_token, _on_progress):
        return chain(inputs)["output_text"]

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    monkeypatch.setattr("backaind.brain.get_knowledge", fake_get_knowledge)
    monkeypatch.setattr("backaind.brain.run_chain_on_multiprocessing", fake_run)

    response = reply(1, "Hi", 1)
    assert response == "Hi,['Hi'],"

    response = reply(1, "Hi", None)
    assert response == "Hi,[],"

    memory = ConversationBufferWindowMemory(k=3)
    memory.chat_memory.add_ai_message("Hi user")
    memory.chat_memory.add_user_message("Hi AI")
    response = reply(1, "Hi", 1, memory)
    assert response == "Hi,['Hi'],AI: Hi user\nHuman: Hi AI"


def test_reply_chooses_the_right_way_of_processing(monkeypatch):
    """Test if the reply function chooses between gipc and multiprocessing."""

    class RunRecorder:
        """Helper class to record the call to run."""

        run_on_gunicorn = False
        run_on_multiprocessing = False

    def fake_get_chain(_ai_id, _updated_environment):
        return (FakeChain(), set(("input_text", "input_knowledge", "input_history")))

    def fake_run_chain_on_multiprocessing(chain, inputs, _on_token, _on_progress):
        RunRecorder.run_on_multiprocessing = True
        return chain(inputs)["output_text"]

    def fake_run_chain_on_gunicorn(chain, inputs, _on_token, _on_progress):
        RunRecorder.run_on_gunicorn = True
        return chain(inputs)["output_text"]

    monkeypatch.setattr("backaind.brain.get_chain", fake_get_chain)
    monkeypatch.setattr(
        "backaind.brain.run_chain_on_multiprocessing", fake_run_chain_on_multiprocessing
    )
    monkeypatch.setattr(
        "backaind.brain.run_chain_on_gunicorn", fake_run_chain_on_gunicorn
    )

    response = reply(1, "Hi", None)
    assert response == "Hi,[],"
    assert RunRecorder.run_on_multiprocessing
    assert not RunRecorder.run_on_gunicorn

    RunRecorder.run_on_multiprocessing = False
    RunRecorder.run_on_gunicorn = False

    with UpdatedEnvironment({"SERVER_SOFTWARE": "gunicorn"}):
        response = reply(1, "Hi", None)
        assert response == "Hi,[],"
        assert not RunRecorder.run_on_multiprocessing
        assert RunRecorder.run_on_gunicorn


def test_run_chain_on_gunicorn(monkeypatch):
    """Test if the runner function for gipc works."""

    def fake_start_process(**kwargs):
        kwargs["args"][2].put(None)
        kwargs["args"][2].put(("prompts", ["testprompt"]))
        kwargs["args"][2].put(None)
        kwargs["args"][2].put(None)
        kwargs["args"][2].put(("token", "testtoken1"))
        kwargs["args"][2].put(("token", "testtoken2"))
        kwargs["args"][2].put(("test", "test"))
        kwargs["args"][2].put(("done", "testtext"))

    class FakeTimeout:
        """Helper class to mock a timeout."""

        def __init__(self, seconds, exception) -> None:
            pass

        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    class OnTokenRecorder:
        """Helper class to record the call to on_token."""

        token = None

    def fake_on_token(token):
        OnTokenRecorder.token = token

    def fake_on_progress(_progress):
        pass

    monkeypatch.setattr("gipc.start_process", fake_start_process)
    monkeypatch.setattr("gevent.Timeout", FakeTimeout)

    text = run_chain_on_gunicorn(
        FakeChain(),
        {"input_text": "Hi", "input_knowledge": "", "input_history": ""},
        None,
        None,
    )
    assert OnTokenRecorder.token is None
    assert text == "testtext"

    text = run_chain_on_gunicorn(
        FakeChain(),
        {"input_text": "Hi", "input_knowledge": "", "input_history": ""},
        fake_on_token,
        fake_on_progress,
    )
    assert OnTokenRecorder.token == "testtoken2"
    assert text == "testtext"


def test_run_chain_on_multiprocessing(monkeypatch):
    """Test if the runner function for multiprocessing works."""

    def fake_process(**_kwargs):
        class FakeProcess:
            """Helper class to mock a multiprocessing process."""

            def start(self):
                """Does nothing, but is called by the runner."""

        return FakeProcess()

    def fake_queue():
        class FakeQueue:
            """Helper class to mock a multiprocessing queue."""

            returns = [
                None,
                ("prompts", ["testprompt"]),
                None,
                None,
                ("token", "testtoken1"),
                ("token", "testtoken2"),
                ("other", "test"),
                ("done", "testtext"),
            ]
            index = 0

            def get(self, _block, _timeout):
                """Return the next test item."""
                current = self.returns[self.index]
                self.index += 1
                if current is None:
                    raise queue.Empty()
                return current

        return FakeQueue()

    class OnTokenRecorder:
        """Helper class to record the call to on_token."""

        token = None

    def fake_on_token(token):
        OnTokenRecorder.token = token

    def fake_on_progress(_progress):
        pass

    monkeypatch.setattr("backaind.brain.global_chain_ppwps", 1)
    monkeypatch.setattr("multiprocessing.Process", fake_process)
    monkeypatch.setattr("multiprocessing.Queue", fake_queue)

    text = run_chain_on_multiprocessing(
        FakeChain(),
        {"input_text": "Hi", "input_knowledge": "", "input_history": ""},
        None,
        None,
    )
    assert OnTokenRecorder.token is None
    assert text == "testtext"

    text = run_chain_on_multiprocessing(
        FakeChain(),
        {"input_text": "Hi", "input_knowledge": "", "input_history": ""},
        fake_on_token,
        fake_on_progress,
    )
    assert OnTokenRecorder.token == "testtoken2"
    assert text == "testtext"


def test_run_chain_process():
    """Test if run_chain_process puts the results in the queue."""
    result_queue = queue.Queue()
    run_chain_process(
        FakeChain(),
        {"input_text": "Hi", "input_knowledge": "", "input_history": ""},
        result_queue,
    )
    result_type, result = result_queue.get()
    assert result_type == "prompts"
    assert result == ["testprompt"]
    result_type, result = result_queue.get()
    assert result_type == "token"
    assert result == "testtoken"
    result_type, result = result_queue.get()
    assert result_type == "done"
    assert result == "Hi,,"


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


def test_estimate_processing_time(monkeypatch):
    """Test if the processing time is estimated correctly."""
    monkeypatch.setattr("backaind.brain.global_chain_ppwps", 2)
    assert estimate_processing_time("Hi") == 1
    assert estimate_processing_time("Hi Hi") == 1
    assert estimate_processing_time("Hi Hi Hi") == 1
    assert estimate_processing_time("Hi Hi Hi Hi") == 2


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
