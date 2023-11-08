"""Workshop is the place to invent, build, edit and work on AIs."""
from flask import Blueprint, render_template
from backaind.auth import login_required

bp = Blueprint("workshop", __name__, url_prefix="/workshop")


@bp.route("/")
@bp.route("/ai/")
@bp.route("/ai/<_id>")
@login_required
def ai(_id=None):
    """Render the AI workshop view."""
    return render_template("workshop/ai.html")


@bp.route("/knowledge/")
@bp.route("/knowledge/<_id>")
@login_required
def knowledge(_id=None):
    """Render the knowledge workshop view."""
    return render_template("workshop/knowledge.html")
