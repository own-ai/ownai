"""Provide AI data processing capabilities."""
from langchain.chains.loading import load_chain_from_config
from flask import current_app, session

from backaind.aifile import read_aifile_from_path, get_input_keys
from backaind.knowledge import get_knowledge


def get_chain():
    """Load the AI chain from session or create a new chain if it doesn't exist."""
    chain = session.get("chain")
    chain_input_keys = session.get("chain_input_keys")
    if not chain or not chain_input_keys:
        aifile = read_aifile_from_path(current_app.config["AIFILE"])
        chain_input_keys = get_input_keys(aifile)
        chain = load_chain_from_config(aifile["chain"])
        session["chain"] = chain
        session["chain_input_keys"] = chain_input_keys
    return (chain, chain_input_keys)


def reply(input_text):
    """Run the chain with an input message and return the AI output."""
    (chain, chain_input_keys) = get_chain()
    inputs = {}
    for input_key in chain_input_keys:
        if input_key == "input_text":
            inputs["input_text"] = input_text
        elif input_key == "input_knowledge":
            knowledge = get_knowledge()
            inputs["input_knowledge"] = knowledge.similarity_search(input_text)

    return chain(inputs)["output_text"]
