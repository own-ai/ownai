"""Test the Workshop module to work on AIs and knowledge."""
import pytest

EXAMPLE_PATHS = (
    "/workshop/",
    "/workshop/ai/",
    "/workshop/ai/new",
    "/workshop/ai/2",
    "/workshop/knowledge/",
    "/workshop/knowledge/new",
    "/workshop/knowledge/2",
)


@pytest.mark.parametrize("path", EXAMPLE_PATHS)
def test_login_required(client, path):
    """Test whether login is required to view all workshop paths."""
    response = client.get(path)
    assert response.headers["Location"] == "/auth/login"


@pytest.mark.parametrize("path", EXAMPLE_PATHS)
def test_index(client, auth, path):
    """Test whether the workshop page gets displayed."""
    auth.login()
    response = client.get(path)
    assert b'id="workshop"' in response.data
