"""Provide access to the database."""
import sqlite3

import click
from flask import current_app, g


def get_db():
    """Get the database connection. Create a new connection if it doesn't exist yet."""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(_error):
    """Close the database connection if it exists. Otherwise, do nothing."""
    database = g.pop("db", None)

    if database is not None:
        database.close()


def init_db():
    """Clear the existing data and create new tables."""
    database = get_db()

    with current_app.open_resource("schema.sql") as sql_file:
        database.executescript(sql_file.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register db functions with the application instance."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
