"""Allow interaction with an AI."""
from datetime import datetime
import json
from flask import Blueprint, render_template, session
from flask_socketio import emit, disconnect
from langchain.callbacks.base import BaseCallbackHandler
from langchain.memory import ConversationBufferWindowMemory

from backaind.aifile import get_all_aifiles_from_db
from backaind.auth import login_required
from backaind.brain import reply
from backaind.knowledge import get_all_knowledge_entries_from_db
from backaind.settings import get_settings

bp = Blueprint("ainteraction", __name__)


class AinteractionCallbackHandler(BaseCallbackHandler):
    """Callback handler for events during response generation."""

    def __init__(self, response_id: int) -> None:
        self.response_id = response_id

    def on_chat_model_start(self, serialized, messages, **kwargs):
        pass

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        send_next_token(self.response_id, token)


@bp.route("/")
@login_required
def index():
    """Render the main ainteraction view."""
    aifiles = get_all_aifiles_from_db()
    ailist = []
    for aifile in aifiles:
        ailist.append(
            {
                "id": aifile["id"],
                "name": aifile["name"],
                "input_keys": json.loads(aifile["input_keys"]),
            }
        )
    knowledge_entries = get_all_knowledge_entries_from_db()
    knowledge_list = []
    for knowledge_entry in knowledge_entries:
        knowledge_list.append(
            {
                "id": knowledge_entry["id"],
                "name": knowledge_entry["name"],
            }
        )

    return render_template(
        "ainteraction/index.html",
        ais=json.dumps(ailist),
        knowledges=json.dumps(knowledge_list),
    )


def handle_incoming_message(message):
    """Handle an incoming socket.io message from a user."""
    if not session.get("user_id"):
        disconnect()
        return

    response_id = message.get("responseId")
    ai_id = message.get("aiId")
    knowledge_id = message.get("knowledgeId")
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
            [AinteractionCallbackHandler(response_id)],
            get_settings(session.get("user_id", -1)).get("external-providers", {}),
        )
        send_response(response_id, response.strip())
    # pylint: disable=broad-exception-caught
    except Exception as exception:
        send_response(response_id, str(exception), "error")
        raise exception


def init_app(app):
    """Register handling of incoming socket.io messages."""
    app.extensions["socketio"].on("message")(handle_incoming_message)


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
