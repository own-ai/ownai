"""Allow interaction with an AI."""
from datetime import datetime
from flask import Blueprint, render_template, session
from flask_socketio import emit, disconnect

from backaind.auth import login_required
from backaind.brain import reply

bp = Blueprint('ainteraction', __name__)

@bp.route('/')
@login_required
def index():
    """Render the main ainteraction view."""
    return render_template('ainteraction/index.html')

def handle_incoming_message(message):
    """Handle an incoming socket.io message from a user."""
    if not session.get('user_id'):
        disconnect()
        return

    response_id = message.get('responseId')
    message_text = message.get('message', {}).get('text', '')
    response = reply(message_text)

    send_response(response_id, response)

def init_app(app):
    """Register handling of incoming socket.io messages."""
    app.extensions['socketio'].on('message')(handle_incoming_message)

def send_next_token(response_id: int, token_text: str):
    """Send the next response token to the user."""
    emit('token', {
        'messageId': response_id,
        'text': token_text,
    })

def send_response(response_id: int, message_text: str):
    """Send the full response message to the user."""
    emit('message', {
        'id': response_id,
        'author': {
            'species': 'ai',
        },
        'date': datetime.now().isoformat(),
        'text': message_text,
        'status': 'done',
    })
