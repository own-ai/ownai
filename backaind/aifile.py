"""Functions to read and validate Aifiles."""
import json
import click
from backaind.db import get_db

MAX_AIFILEVERSION = 1


class InvalidAifileError(Exception):
    """The Aifile has invalid or missing data."""


def validate_aifile(aifile):
    """Validate an Aifile for required fields and correct version."""
    required_fields = ["name", "aifileversion", "chain"]
    allowed_input_keys = ["input_text", "input_knowledge", "input_history"]

    for field in required_fields:
        if field not in aifile:
            raise InvalidAifileError(f"Missing field in aifile: {field}")

    for input_key in get_input_keys(aifile):
        if input_key not in allowed_input_keys:
            raise InvalidAifileError(f"Unknown input key: {input_key}")

    if aifile["aifileversion"] > MAX_AIFILEVERSION:
        raise InvalidAifileError("This aifile requires a newer version of ownAI.")


def get_input_keys(aifile):
    """Get all input keys for an aifile."""

    def iterate_json_key_values(json_obj, key_prefix=""):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                new_key_prefix = f"{key_prefix}.{key}" if key_prefix else key
                if isinstance(value, (dict, list)):
                    yield from iterate_json_key_values(value, new_key_prefix)
                else:
                    yield (new_key_prefix, value)
        elif isinstance(json_obj, list):
            for index, value in enumerate(json_obj):
                new_key_prefix = f"{key_prefix}[{index}]"
                if isinstance(value, (dict, list)):
                    yield from iterate_json_key_values(value, new_key_prefix)
                else:
                    yield (new_key_prefix, value)

    input_keys = set()
    for key, value in iterate_json_key_values(aifile):
        if ("input_key" in key or "input_variables" in key) and value.startswith(
            "input_"
        ):
            input_keys.add(value)
    return input_keys


def read_aifile_from_path(aifile_path):
    """Read an Aifile from the given path and validate its data. Return the Aifile as dictionary."""
    with open(aifile_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    validate_aifile(data)
    return data


def get_aifile_from_db(ai_id):
    """Return the Aifile data from the database."""
    database = get_db()
    aifile = database.execute("SELECT * FROM ai WHERE id = ?", (ai_id,)).fetchone()
    return aifile


def get_all_aifiles_from_db():
    """Return all Aifiles from the database."""
    database = get_db()
    aifiles = database.execute("SELECT * FROM ai").fetchall()
    return aifiles


@click.command("add-ai")
@click.option("--aifile", "aifile_path", prompt="Aifile to import")
def add_ai(aifile_path):
    """Register a new AI or update an AI with the same name."""
    database = get_db()
    aifile = read_aifile_from_path(aifile_path)
    name = aifile["name"]
    input_keys_json = json.dumps(list(get_input_keys(aifile)))
    chain = json.dumps(aifile["chain"])

    existing_ai = database.execute(
        "SELECT * FROM ai WHERE name = ?", (name,)
    ).fetchone()

    if existing_ai is None:
        database.execute(
            "INSERT INTO ai (name, input_keys, chain) VALUES (?, ?, ?)",
            (name, input_keys_json, chain),
        )
        database.commit()
        click.echo(f"Added {name}. Say hello!")
    else:
        database.execute(
            "UPDATE ai SET input_keys = ?, chain = ? WHERE name = ?",
            (input_keys_json, chain, name),
        )
        database.commit()
        click.echo(f"Updated {name}. Say hello!")


def init_app(app):
    """Register CLI commands with the application instance."""
    app.cli.add_command(add_ai)
