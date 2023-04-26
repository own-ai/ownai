"""Test the authentication."""
import pytest
from flask import g, session

from backaind.auth import register_user
from backaind.db import get_db

def test_login(client, auth):
    """Test whether login works and redirects to index page."""
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == '/'

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'

@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username or password.'),
    ('test', 'a', b'Incorrect username or password.'),
))
def test_login_validate_input(auth, username, password, message):
    """Test whether entering invalid credentials returns an error message."""
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    """Test whether logout removes the user from session."""
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session

def test_register_user_command(app, runner):
    """Test whether registering a new user works."""
    username = 'a-new-user'
    password = 'a-password'
    with app.app_context():
        database = get_db()

        user = database.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        assert user is None

        result = runner.invoke(register_user, input=f'{username}\n{password}\n{password}\n')
        assert 'Registration successful' in result.output
        user = database.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        assert user is not None

        result = runner.invoke(register_user, input=f'{username}\n{password}\n{password}\n')
        assert 'already registered' in result.output