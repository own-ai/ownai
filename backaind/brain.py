"""Provide AI data processing capabilities."""
import json
from threading import Lock
from typing import Tuple, Set
from langchain.chains.base import Chain
from langchain.chains.loading import load_chain_from_config

from backaind.aifile import get_aifile_from_db
from backaind.knowledge import get_knowledge

# pylint: disable=invalid-name
global_chain = None
global_chain_id = None
global_chain_input_keys = None
# pylint: enable=invalid-name
chain_lock = Lock()


def get_chain(ai_id: int) -> Tuple[Chain, Set[str]]:
    """Load the AI chain or create a new chain if it doesn't exist."""
    # pylint: disable=global-statement
    global global_chain, global_chain_id, global_chain_input_keys
    with chain_lock:
        chain = global_chain
        chain_id = global_chain_id
        chain_input_keys = global_chain_input_keys
        if not chain or not chain_input_keys or chain_id != ai_id:
            aifile = get_aifile_from_db(ai_id)
            chain_input_keys = json.loads(aifile["input_keys"])
            chain = load_chain_from_config(json.loads(aifile["chain"]))
            global_chain = chain
            global_chain_id = ai_id
            global_chain_input_keys = chain_input_keys
    return (chain, chain_input_keys)


def reset_global_chain(ai_id=None):
    """
    Drop the global chain instance.
    If ai_id is set, it only drops the global chain instance if it matches this ID.
    """
    # pylint: disable=global-statement
    global global_chain, global_chain_id, global_chain_input_keys
    with chain_lock:
        if not ai_id or ai_id == global_chain_id:
            global_chain = None
            global_chain_id = None
            global_chain_input_keys = None


def reply(ai_id: int, input_text: str, knowledge_id: int | None = None) -> str:
    """Run the chain with an input message and return the AI output."""
    (chain, chain_input_keys) = get_chain(ai_id)
    inputs = {}
    for input_key in chain_input_keys:
        if input_key == "input_text":
            inputs["input_text"] = input_text
        elif input_key == "input_knowledge":
            if knowledge_id is None:
                inputs["input_knowledge"] = []
            else:
                knowledge = get_knowledge(knowledge_id)
                inputs["input_knowledge"] = knowledge.similarity_search(input_text)

    return chain(inputs)["output_text"]
