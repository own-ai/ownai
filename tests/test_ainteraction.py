"""Test the Ainteraction module to interact with AI applications."""
import pytest

@pytest.mark.parametrize('path', (
    '/',
))
def test_login_required(client, path):
    """Test whether a login is required to view path."""
    response = client.get(path)
    assert response.headers['Location'] == '/auth/login'

def test_index(client, auth):
    """Test whether the coming soon page gets displayed."""
    auth.login()
    response = client.get('/')
    assert b'Hello' in response.data
    assert b'Coming soon' in response.data
