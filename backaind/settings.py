"""Allow users to see and change their settings."""
from flask import Blueprint, request, flash, render_template, g
from backaind.auth import login_required, is_password_correct, set_password

bp = Blueprint("settings", __name__, url_prefix="/settings")


@bp.route("/password", methods=("GET", "POST"))
@login_required
def password():
    """Render the password change page or change the user's password."""
    if request.method == "POST":
        current_password = request.form["current-password"]
        new_password = request.form["new-password"]
        new_password_confirmation = request.form["new-password-confirmation"]

        if new_password != new_password_confirmation:
            flash("Password and confirmation do not match.", "danger")
        elif not is_password_correct(g.user["username"], current_password):
            flash("Incorrect current password.", "danger")
        elif len(new_password) < 10:
            flash("Password must be at least 10 characters long.", "danger")
        else:
            set_password(g.user["username"], new_password)
            flash("Password changed successfully.", "success")

    return render_template("settings/password.html")
