"""Provide AI data processing capabilities."""
from langchain.chains.loading import load_chain_from_config
from flask import current_app, session

from backaind.aifile import read_aifile_from_path

def get_chain():
    """Load the AI chain from session or create a new chain if it doesn't exist."""
    chain = session.get('chain')
    if not chain:
        aifile = read_aifile_from_path(current_app.config['AIFILE'])
        chain = load_chain_from_config(aifile['chain'])
        session['chain'] = chain
    return chain

def reply(message):
    """Run the chain with an input message and return the AI output."""
    chain = get_chain()
    return chain.run(message).strip()
