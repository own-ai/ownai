"""Functions to read and validate Aifiles."""
import json

import click
from flask import current_app

from .extensions import db
from .models import Ai

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


@click.command("add-ai")
@click.option("--aifile", "aifile_path", prompt="Aifile to import")
def add_ai(aifile_path):
    """Register a new AI or update an AI with the same name."""
    aifile = read_aifile_from_path(aifile_path)
    name = aifile["name"]
    input_keys = list(get_input_keys(aifile))
    input_labels = aifile.get("input_labels")
    chain = aifile["chain"]
    greeting = aifile.get("greeting")

    existing_ai = db.session.query(Ai).filter_by(name=name).first()

    if existing_ai is None:
        new_ai = Ai(
            name=name,
            input_keys=input_keys,
            input_labels=input_labels,
            chain=chain,
            greeting=greeting,
        )
        db.session.add(new_ai)
        db.session.commit()
        click.echo(f"Added {name}. Say hello!")
    else:
        existing_ai.input_keys = input_keys
        existing_ai.input_labels = input_labels
        existing_ai.chain = chain
        existing_ai.greeting = greeting
        existing_ai.name = name
        db.session.commit()
        click.echo(f"Updated {name}. Say hello!")


@click.command("download-model")
@click.option("--repo", "repo_id", prompt="Hugging Face Repository ID")
@click.option("--filename", "filename", prompt="File within the repository")
def download_model(repo_id, filename):
    """Download a model from Hugging Face and save it to the instance folder."""
    # pylint: disable-next=import-outside-toplevel
    from huggingface_hub import hf_hub_download

    hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=current_app.instance_path,
        local_dir_use_symlinks=True,
    )


def init_app(app):
    """Register CLI commands with the application instance."""
    app.cli.add_command(add_ai)
    app.cli.add_command(download_model)
