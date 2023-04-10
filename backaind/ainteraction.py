"""Allow interaction with an AI."""
from flask import (
    Blueprint, render_template
)

from backaind.auth import login_required

bp = Blueprint('ainteraction', __name__)

@bp.route('/')
@login_required
def index():
    """Render the main ainteraction view."""
    return render_template('ainteraction/index.html')
