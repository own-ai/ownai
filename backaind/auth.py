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
from sqlalchemy import exc
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db
from .models import User


bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Render the login page or login a user."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = db.session.query(User).filter_by(username=username).first()

        if user is None or not check_password_hash(user.passhash, password):
            flash("Incorrect username or password.", "danger")
        else:
            session.clear()
            session["user_id"] = user.id
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
        g.user = db.session.get(User, user_id)


def is_password_correct(username: str, password: str):
    """Check if the password for the given user is correct."""
    user = db.session.query(User).filter_by(username=username).first()

    return user is not None and check_password_hash(user.passhash, password)


def set_password(username: str, password: str):
    """Set the (new) password for an user."""
    user = db.session.query(User).filter_by(username=username).one()
    user.passhash = generate_password_hash(password)
    db.session.commit()


def login_required(view):
    """
    Wrap a view to instead redirect to login page if the user is not logged in.
    For API requests, this does not redirect, but returns a 401 Unauthorized status code.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.get("user") is None:
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
    try:
        user = User(username=username, passhash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
    except exc.IntegrityError as exception:
        raise click.ClickException(
            f"User {username} is already registered."
        ) from exception

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
