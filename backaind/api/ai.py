"""API to create, read, update and delete AIs."""
import json
from flask import Blueprint, jsonify, request, make_response, abort
from backaind.aifile import get_all_aifiles_from_db, get_aifile_from_db
from backaind.auth import login_required
from backaind.brain import reset_global_chain
from backaind.db import get_db

bp = Blueprint("api-ai", __name__, url_prefix="/api/ai")


def validate(ai_json):
    """Validate if the JSON is valid for an AI entry."""
    if not ai_json:
        abort(make_response(jsonify(error="The AI file cannot be empty."), 400))
    if not "name" in ai_json:
        abort(make_response(jsonify(error='The property "name" is required.'), 400))
    if not isinstance(ai_json["name"], str):
        abort(
            make_response(jsonify(error='The property "name" has to be a string.'), 400)
        )
    if not "input_keys" in ai_json:
        abort(
            make_response(jsonify(error='The property "input_keys" is required.'), 400)
        )
    if not isinstance(ai_json["input_keys"], list):
        abort(
            make_response(
                jsonify(error='The property "input_keys" has to be a list of strings.'),
                400,
            )
        )
    if not "chain" in ai_json:
        abort(make_response(jsonify(error='The property "chain" is required.'), 400))
    if not isinstance(ai_json["chain"], dict):
        abort(
            make_response(
                jsonify(error='The property "chain" has to be a chain object.'), 400
            )
        )


@bp.route("/", methods=["GET"])
@login_required
def get_all_ais():
    """Get all AIs."""
    aifiles = [
        {
            **ai,
            "chain": json.loads(ai["chain"]),
            "input_keys": json.loads(ai["input_keys"]),
        }
        for ai in get_all_aifiles_from_db()
    ]
    return jsonify(aifiles)


@bp.route("/<int:ai_id>", methods=["GET"])
@login_required
def get_ai(ai_id):
    """Get a specific AI."""
    aifile = get_aifile_from_db(ai_id)
    if aifile is None:
        abort(404)
    return jsonify(
        {
            **aifile,
            "chain": json.loads(aifile["chain"]),
            "input_keys": json.loads(aifile["input_keys"]),
        }
    )


@bp.route("/", methods=["POST"])
@login_required
def create_ai():
    """Create a new AI."""
    validate(request.json)
    assert request.json

    database = get_db()
    name = request.json["name"]
    input_keys = json.dumps(request.json["input_keys"])
    chain = json.dumps(request.json["chain"])
    ai_id = database.execute(
        "INSERT INTO ai (name, input_keys, chain) VALUES (?, ?, ?)",
        (name, input_keys, chain),
    ).lastrowid
    database.commit()
    return (
        jsonify(
            {
                "id": ai_id,
                "name": name,
                "input_keys": request.json["input_keys"],
                "chain": request.json["chain"],
            }
        ),
        201,
    )


@bp.route("/<int:ai_id>", methods=["PUT"])
@login_required
def update_ai(ai_id):
    """Update an AI."""
    validate(request.json)
    assert request.json

    database = get_db()
    name = request.json["name"]
    input_keys = json.dumps(request.json["input_keys"])
    chain = json.dumps(request.json["chain"])
    database.execute(
        "UPDATE ai SET name = ?, input_keys = ?, chain = ? WHERE id = ?",
        (name, input_keys, chain, ai_id),
    )
    database.commit()
    reset_global_chain(ai_id)
    return jsonify(
        {
            "id": ai_id,
            "name": name,
            "input_keys": request.json["input_keys"],
            "chain": request.json["chain"],
        }
    )


@bp.route("/<int:ai_id>", methods=["DELETE"])
@login_required
def delete_ai(ai_id):
    """Delete an AI."""
    database = get_db()
    database.execute("DELETE FROM ai WHERE id = ?", (ai_id,))
    database.commit()
    reset_global_chain(ai_id)
    return ("", 204)
