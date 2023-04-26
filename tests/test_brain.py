"""Test the handling of AI chains."""
from flask import session

from backaind.brain import get_chain, reply

def test_get_chain_returns_from_session(client):
    """Test if the chain is loaded from session."""
    with client:
        client.get('/')
        session['chain'] = 'NotARealChain'
        chain = get_chain()
        assert chain == 'NotARealChain'

def test_get_chain_creates_new_chain_if_not_in_session(client, monkeypatch):
    """Test if the chain gets created if it doesn't exist yet."""
    with client:
        client.get('/')
        session['chain'] = None
        monkeypatch.setattr('backaind.brain.read_aifile_from_path', lambda _path: {
            'chain': 'NotARealChain'
        })
        monkeypatch.setattr('backaind.brain.load_chain_from_config', lambda chain: chain)
        chain = get_chain()
        assert chain == 'NotARealChain'
        assert session['chain'] == 'NotARealChain'

def test_reply_runs_the_chain(monkeypatch):
    """Test if the reply function calls the chain."""
    class FakeChain:
        """Helper class to allow call to chain.run()."""
        def run(self, _message):
            """Mock function for chain.run()."""
            return 'Response'

    def fake_get_chain():
        return FakeChain()

    monkeypatch.setattr('backaind.brain.get_chain', fake_get_chain)
    response = reply('Hi')

    assert response == 'Response'
