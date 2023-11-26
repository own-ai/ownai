"""Allow interaction with an AI."""
from datetime import datetime
import json

from flask import Blueprint, render_template, session, g, redirect, url_for
from flask_socketio import emit, disconnect
from langchain.memory import ConversationBufferWindowMemory

from .brain import reply
from .extensions import db, socketio
from .models import Ai, Knowledge
from .settings import get_settings

bp = Blueprint("ainteraction", __name__)


@bp.route("/")
@bp.route("/<_ai>")
def index(_ai=None):
    """Render the main ainteraction view."""
    is_public = g.get("user") is None
    ais = get_ai_data(only_public=is_public)

    if is_public and not ais:
        return redirect(url_for("auth.login"))

    return render_template(
        "ainteraction/index.html",
        ais=json.dumps(ais),
        knowledges=json.dumps(get_knowledge_data(only_public=is_public)),
    )


def handle_incoming_message(message):
    """Handle an incoming socket.io message from a user."""
    is_public = session.get("user_id") is None
    ai_id = message.get("aiId")
    knowledge_id = message.get("knowledgeId")

    if not ai_id:
        disconnect()
        return

    if is_public and not is_ai_public(ai_id):
        disconnect()
        return

    if is_public and knowledge_id and not is_knowledge_public(knowledge_id):
        disconnect()
        return

    response_id = message.get("responseId")
    message_text = message.get("message", {}).get("text", "")

    memory = ConversationBufferWindowMemory(k=3)
    for history_message in message.get("history", []):
        if history_message.get("author", {}).get("species") == "ai":
            memory.chat_memory.add_ai_message(history_message.get("text", ""))
        else:
            memory.chat_memory.add_user_message(history_message.get("text", ""))

    try:
        response = reply(
            ai_id,
            message_text,
            knowledge_id,
            memory,
            lambda token: send_next_token(response_id, token),
            lambda progress: send_progress(response_id, progress),
            get_settings(session.get("user_id", -1)).get("external-providers", {}),
        )
        send_response(response_id, response.strip())
    # pylint: disable=broad-exception-caught
    except Exception as exception:
        send_response(response_id, str(exception), "error")
        raise exception


def init_app(_app):
    """Register handling of incoming socket.io messages."""
    socketio.on("message")(handle_incoming_message)


def get_ai_data(only_public=True):
    """Get data for all AIs."""
    ai_query = db.session.query(Ai)
    if only_public:
        ai_query = ai_query.filter_by(is_public=True)
    return [
        {
            "id": ai.id,
            "name": ai.name,
            "input_keys": ai.input_keys,
            "input_labels": ai.input_labels,
            "greeting": ai.greeting,
        }
        for ai in ai_query.all()
    ]


def get_knowledge_data(only_public=True):
    """Get data for all knowledges."""
    knowledge_query = db.session.query(Knowledge)
    if only_public:
        knowledge_query = knowledge_query.filter_by(is_public=True)
    return [
        {
            "id": knowledge.id,
            "name": knowledge.name,
        }
        for knowledge in knowledge_query.all()
    ]


def is_ai_public(ai_id: int):
    """Check if an AI is public."""
    ai = db.session.get(Ai, ai_id)
    return bool(ai and ai.is_public)


def is_knowledge_public(knowledge_id: int):
    """Check if a knowledge is public."""
    knowledge = db.session.get(Knowledge, knowledge_id)
    return bool(knowledge and knowledge.is_public)


def send_progress(response_id: int, progress: int):
    """Send the current progress to the user."""
    emit(
        "progress",
        {
            "messageId": response_id,
            "progress": progress,
        },
    )


def send_next_token(response_id: int, token_text: str):
    """Send the next response token to the user."""
    emit(
        "token",
        {
            "messageId": response_id,
            "text": token_text,
        },
    )


def send_response(response_id: int, message_text: str, status: str = "done"):
    """Send the full response message to the user."""
    emit(
        "message",
        {
            "id": response_id,
            "author": {
                "species": "ai",
            },
            "date": datetime.now().isoformat(),
            "text": message_text,
            "status": status,
        },
    )
