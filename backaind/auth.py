"""Provide user authentication and registration."""
import functools

import click
from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from backaind.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Render the login page or login a user."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        database = get_db()
        user = database.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["passhash"], password):
            flash("Incorrect username or password.", "danger")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Logout the current user and redirect to index page."""
    session.clear()
    return redirect(url_for("index"))


@bp.before_app_request
def load_logged_in_user():
    """Load the current user and add it to the global g instance."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


def is_password_correct(username: str, password: str):
    """Check if the password for the given user is correct."""
    database = get_db()
    user = database.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()

    return user is not None and check_password_hash(user["passhash"], password)


def set_password(username: str, password: str):
    """Set the (new) password for an user."""
    database = get_db()
    database.execute(
        "UPDATE user SET passhash = ? WHERE username = ?",
        (generate_password_hash(password), username),
    )
    database.commit()


def login_required(view):
    """
    Wrap a view to instead redirect to login page if the user is not logged in.
    For API requests, this does not redirect, but returns a 401 Unauthorized status code.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            if request.path.startswith("/api/"):
                abort(401)
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@click.command("add-user")
@click.option("--username", prompt="User name")
@click.password_option()
def add_user(username, password):
    """Register a new user for the application."""
    database = get_db()

    try:
        database.execute(
            "INSERT INTO user (username, passhash) VALUES (?, ?)",
            (username, generate_password_hash(password)),
        )
        database.commit()
    except database.IntegrityError as exc:
        raise click.ClickException(f"User {username} is already registered.") from exc

    click.echo(f"Registration successful. Hello {username}, nice to meet you!")


@click.command("set-password")
@click.option("--username", prompt="User name")
@click.password_option()
def set_password_command(username, password):
    """Command to set the (new) password for an user."""
    set_password(username, password)
    click.echo(f"Successfully set the password for {username}.")


def init_app(app):
    """Register auth CLI commands with the application instance."""
    app.cli.add_command(add_user)
    app.cli.add_command(set_password_command)
