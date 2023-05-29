"""Workshop is the place to invent, build, edit and work on AIs."""
from flask import Blueprint, render_template
from backaind.auth import login_required

bp = Blueprint("workshop", __name__, url_prefix="/workshop")


@bp.route("/")
@bp.route("/ai/")
@bp.route("/ai/<_id>")
@bp.route("/knowledge/")
@bp.route("/knowledge/<_id>")
@login_required
def index(_id=None):
    """Render the main workshop view."""
    return render_template("workshop/index.html")
