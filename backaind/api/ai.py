"""API to create, read, update and delete AIs."""
from flask import Blueprint, jsonify, request, make_response, abort

from ..auth import login_required, login_required_allow_demo
from ..brain import reset_global_chain
from ..extensions import db
from ..models import Ai

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
@login_required_allow_demo
def get_all_ais():
    """Get all AIs."""
    return [ai.as_dict() for ai in db.session.query(Ai).all()]


@bp.route("/<int:ai_id>", methods=["GET"])
@login_required_allow_demo
def get_ai(ai_id):
    """Get a specific AI."""
    aifile = db.get_or_404(Ai, ai_id)
    return aifile.as_dict()


@bp.route("/", methods=["POST"])
@login_required
def create_ai():
    """Create a new AI."""
    validate(request.json)
    assert request.json

    name = request.json["name"]
    input_keys = request.json["input_keys"]
    chain = request.json["chain"]
    new_ai = Ai(name=name, input_keys=input_keys, chain=chain)
    db.session.add(new_ai)
    db.session.commit()
    return (
        jsonify(new_ai.as_dict()),
        201,
    )


@bp.route("/<int:ai_id>", methods=["PUT"])
@login_required
def update_ai(ai_id):
    """Update an AI."""
    validate(request.json)
    assert request.json

    name = request.json["name"]
    input_keys = request.json["input_keys"]
    chain = request.json["chain"]

    existing_ai = db.get_or_404(Ai, ai_id)
    existing_ai.name = name
    existing_ai.input_keys = input_keys
    existing_ai.chain = chain
    db.session.commit()
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
    existing_ai = db.get_or_404(Ai, ai_id)
    db.session.delete(existing_ai)
    db.session.commit()
    reset_global_chain(ai_id)
    return ("", 204)
