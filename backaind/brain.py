"""Provide AI data processing capabilities."""
import os
import queue
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains.base import Chain
from langchain.chains.loading import load_chain_from_config
from langchain.llms.huggingface_text_gen_inference import HuggingFaceTextGenInference
from langchain.schema import BaseMemory

from backaind.extensions import db
from backaind.knowledge import get_knowledge
from backaind.models import Ai

DEFAULT_PPWPS = 2.0
# pylint: disable=invalid-name
global_chain = None
global_chain_id = None
global_chain_input_keys = None
# prompt processing words per second
global_chain_ppwps = DEFAULT_PPWPS
# pylint: enable=invalid-name
chain_lock = Lock()


def get_chain(
    ai_id: int, updated_environment: Optional[dict] = None
) -> Tuple[Chain, Set[str]]:
    """Load the AI chain or create a new chain if it doesn't exist."""
    # pylint: disable=global-statement
    global global_chain, global_chain_id, global_chain_input_keys, global_chain_ppwps
    with chain_lock:
        chain = global_chain
        chain_id = global_chain_id
        chain_input_keys = global_chain_input_keys
        if not chain or not chain_input_keys or chain_id != ai_id:
            aifile = db.get_or_404(Ai, ai_id)
            chain_input_keys = aifile.input_keys
            with UpdatedEnvironment(updated_environment or {}):
                chain = load_chain_from_config(aifile.chain)
            set_text_generation_inference_token(chain)
            global_chain = chain
            global_chain_id = ai_id
            global_chain_input_keys = chain_input_keys
            global_chain_ppwps = DEFAULT_PPWPS
    return (chain, chain_input_keys)


def reset_global_chain(ai_id=None):
    """
    Drop the global chain instance.
    If ai_id is set, it only drops the global chain instance if it matches this ID.
    """
    # pylint: disable=global-statement
    global global_chain, global_chain_id, global_chain_input_keys, global_chain_ppwps
    with chain_lock:
        if not ai_id or ai_id == global_chain_id:
            global_chain = None
            global_chain_id = None
            global_chain_input_keys = None
            global_chain_ppwps = DEFAULT_PPWPS


def reply(
    ai_id: int,
    input_text: str,
    knowledge_id: Optional[int] = None,
    memory: Optional[BaseMemory] = None,
    on_token: Optional[Callable[[str], None]] = None,
    on_progress: Optional[Callable[[int], None]] = None,
    updated_environment: Optional[dict] = None,
) -> str:
    """Run the chain with an input message and return the AI output."""
    (chain, chain_input_keys) = get_chain(ai_id, updated_environment)
    inputs = {}
    has_memory = (
        memory
        and "input_history" in chain_input_keys
        and memory.load_memory_variables({})["history"]
    )
    for input_key in chain_input_keys:
        if input_key == "input_text":
            inputs["input_text"] = input_text
        elif input_key == "input_knowledge":
            if knowledge_id is None:
                inputs["input_knowledge"] = []
            else:
                with UpdatedEnvironment({"TOKENIZERS_PARALLELISM": "false"}):
                    knowledge = get_knowledge(knowledge_id)
                    inputs["input_knowledge"] = knowledge.similarity_search(
                        input_text, k=1 if has_memory else 4
                    )
        elif input_key == "input_history":
            if memory is None:
                inputs["input_history"] = ""
            else:
                inputs["input_history"] = memory.load_memory_variables({})["history"]

    if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
        return run_chain_on_gunicorn(chain, inputs, on_token, on_progress)
    return run_chain_on_multiprocessing(chain, inputs, on_token, on_progress)


def run_chain_on_gunicorn(
    chain: Chain,
    inputs: dict,
    on_token: Optional[Callable[[str], None]],
    on_progress: Optional[Callable[[int], None]],
):
    """Run the chain with gipc in the context of gevent."""
    # pylint: disable=import-outside-toplevel
    import gevent
    import gipc

    with gipc.pipe() as (readend, writeend):
        gipc.start_process(
            target=run_chain_process, args=(chain, inputs, writeend), daemon=True
        )
        seconds_estimated = 0
        seconds_passed = 0
        prompt = ""
        updated_global_chain_ppwps = False
        while True:
            message = None
            with gevent.Timeout(1, False) as timeout:
                message = readend.get(timeout=timeout)
            if message is None:
                if seconds_estimated:
                    seconds_passed += 1
                    if on_progress and seconds_passed <= seconds_estimated:
                        on_progress(int(seconds_passed / seconds_estimated * 100))
            else:
                result_type, text = message
                if result_type == "token":
                    if on_token:
                        on_token(text)
                    if not updated_global_chain_ppwps:
                        updated_global_chain_ppwps = True
                        update_global_chain_ppwps(prompt, seconds_passed)
                elif result_type == "done":
                    return text
                elif result_type == "prompts":
                    prompt = "\n".join(text)
                    seconds_estimated = estimate_processing_time(prompt)


def run_chain_on_multiprocessing(
    chain: Chain,
    inputs: dict,
    on_token: Optional[Callable[[str], None]],
    on_progress: Optional[Callable[[int], None]],
):
    """Run the chain with multiprocessing (won't work with gevent)."""
    # pylint: disable-next=import-outside-toplevel
    import multiprocessing

    result_queue = multiprocessing.Queue()
    multiprocessing.Process(
        target=run_chain_process, args=(chain, inputs, result_queue), daemon=True
    ).start()
    seconds_estimated = 0
    seconds_passed = 0
    prompt = ""
    updated_global_chain_ppwps = False
    while True:
        try:
            result_type, text = result_queue.get(True, 1)
            if result_type == "token":
                if on_token:
                    on_token(text)
                if not updated_global_chain_ppwps:
                    updated_global_chain_ppwps = True
                    update_global_chain_ppwps(prompt, seconds_passed)
            elif result_type == "done":
                return text
            elif result_type == "prompts":
                prompt = "\n".join(text)
                seconds_estimated = estimate_processing_time(prompt)
        except queue.Empty:
            if seconds_estimated:
                seconds_passed += 1
                if on_progress and seconds_passed <= seconds_estimated:
                    on_progress(int(seconds_passed / seconds_estimated * 100))


def run_chain_process(chain: Chain, inputs: dict, putable):
    """Run the chain in a separate process and put the results in the putable."""

    class CallbackHandler(BaseCallbackHandler):
        """Callback handler that puts tokens in the putable as they are generated."""

        def on_chat_model_start(self, serialized, messages, **kwargs):
            pass

        def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
        ) -> Any:
            putable.put(("prompts", prompts))

        def on_llm_new_token(self, token: str, **kwargs) -> None:
            putable.put(("token", token))

    output_text = chain(inputs, callbacks=[CallbackHandler()])["output_text"]
    putable.put(("done", output_text))


def find_instances(obj, cls):
    """Find all instances of a class in an object."""
    instances = []
    if isinstance(obj, cls):
        instances.append(obj)
    if isinstance(obj, list):
        for item in obj:
            instances.extend(find_instances(item, cls))
    elif hasattr(obj, "__dict__"):
        for prop in vars(obj).values():
            instances.extend(find_instances(prop, cls))
    return instances


def set_text_generation_inference_token(chain: Chain):
    """Set the token for all HuggingFaceTextGenInference instances in the chain."""
    token = os.environ.get("TEXT_GENERATION_INFERENCE_TOKEN", None)
    if not token:
        return
    all_huggingface_instances = find_instances(chain, HuggingFaceTextGenInference)
    for instance in all_huggingface_instances:
        instance.client.headers = {"Authorization": f"Bearer {token}"}


def estimate_processing_time(prompt: str) -> int:
    """Estimate the processing time for a prompt."""
    return int(len(prompt.split()) / global_chain_ppwps) or 1


def update_global_chain_ppwps(prompt: str, seconds_passed: int):
    """Update the global chain prompt processing words per second score."""
    # pylint: disable=global-statement
    global global_chain_ppwps
    global_chain_ppwps = len(prompt.split()) / (seconds_passed or 1)


class UpdatedEnvironment:
    """Temporarily update the environment variables."""

    def __init__(self, new_values):
        self.new_values = new_values
        self.old_values = {}

    def __enter__(self):
        for key, new_value in self.new_values.items():
            if key in os.environ:
                self.old_values[key] = os.environ[key]
            os.environ[key] = new_value

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key in self.new_values.keys():
            if key in self.old_values:
                os.environ[key] = self.old_values[key]
            else:
                del os.environ[key]
