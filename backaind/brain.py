"""Provide AI data processing capabilities."""
import json
from typing import Tuple, Set
from langchain.chains.base import Chain
from langchain.chains.loading import load_chain_from_config
from flask import session

from backaind.aifile import get_aifile_from_db
from backaind.knowledge import get_knowledge


def get_chain(ai_id: int) -> Tuple[Chain, Set[str]]:
    """Load the AI chain from session or create a new chain if it doesn't exist."""
    chain = session.get(f"chain[{ai_id}]")
    chain_input_keys = session.get(f"chain_input_keys[{ai_id}]")
    if not chain or not chain_input_keys:
        aifile = get_aifile_from_db(ai_id)
        chain_input_keys = json.loads(aifile["input_keys"])
        chain = load_chain_from_config(json.loads(aifile["chain"]))
        session[f"chain[{ai_id}]"] = chain
        session[f"chain_input_keys[{ai_id}]"] = chain_input_keys
    return (chain, chain_input_keys)


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
