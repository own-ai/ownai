"""API to create, read, update and delete knowledge."""
import os
import shutil
import tempfile
import uuid
from flask import Blueprint, jsonify, request, make_response, abort, current_app
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backaind.auth import login_required
from backaind.db import get_db
from backaind.knowledge import (
    add_to_knowledge,
    get_all_knowledge_entries_from_db,
    get_knowledge_entry_from_db,
    reset_global_knowledge,
)

bp = Blueprint("api-knowledge", __name__, url_prefix="/api/knowledge")


def validate(knowledge_json):
    """Validate if the JSON is valid for a knowledge entry."""
    if not knowledge_json:
        abort(make_response(jsonify(error="The knowledge data cannot be empty."), 400))
    if not "name" in knowledge_json:
        abort(make_response(jsonify(error='The property "name" is required.'), 400))
    if not isinstance(knowledge_json["name"], str):
        abort(
            make_response(jsonify(error='The property "name" has to be a string.'), 400)
        )
    if not "embeddings" in knowledge_json:
        abort(
            make_response(jsonify(error='The property "embeddings" is required.'), 400)
        )
    if not knowledge_json["embeddings"] in ("huggingface",):
        abort(make_response(jsonify(error="Unknown embeddings type."), 400))
    if not "chunk_size" in knowledge_json:
        abort(
            make_response(jsonify(error='The property "chunk_size" is required.'), 400)
        )
    if not isinstance(knowledge_json["chunk_size"], int):
        abort(
            make_response(
                jsonify(error='The property "chunk_size" has to be a number.'), 400
            )
        )


@bp.route("/", methods=["GET"])
@login_required
def get_all_knowledge():
    """Get all knowledge."""
    knowledges = [
        {
            "id": knowledge["id"],
            "name": knowledge["name"],
            "embeddings": knowledge["embeddings"],
            "chunk_size": knowledge["chunk_size"],
        }
        for knowledge in get_all_knowledge_entries_from_db()
    ]
    return jsonify(knowledges)


@bp.route("/<int:knowledge_id>", methods=["GET"])
@login_required
def get_knowledge(knowledge_id):
    """Get a specific knowledge entry."""
    knowledge = get_knowledge_entry_from_db(knowledge_id)
    if knowledge is None:
        abort(404)
    return jsonify(
        {
            "id": knowledge["id"],
            "name": knowledge["name"],
            "embeddings": knowledge["embeddings"],
            "chunk_size": knowledge["chunk_size"],
        }
    )


@bp.route("/", methods=["POST"])
@login_required
def create_knowledge():
    """Create a new knowledge entry."""
    validate(request.json)
    assert request.json

    database = get_db()
    name = request.json["name"]
    embeddings = request.json["embeddings"]
    chunk_size = request.json["chunk_size"]
    persist_directory = os.path.join(
        current_app.instance_path, "knowledge-" + uuid.uuid4().hex
    )
    os.makedirs(persist_directory)

    knowledge_id = database.execute(
        """
        INSERT INTO knowledge (name, embeddings, chunk_size, persist_directory)
        VALUES (?, ?, ?, ?)
        """,
        (name, embeddings, chunk_size, persist_directory),
    ).lastrowid
    database.commit()
    return (
        jsonify(
            {
                "id": knowledge_id,
                "name": name,
                "embeddings": embeddings,
                "chunk_size": chunk_size,
            }
        ),
        201,
    )


@bp.route("/<int:knowledge_id>", methods=["PUT"])
@login_required
def update_knowledge(knowledge_id):
    """Update a knowledge entry."""
    validate(request.json)
    assert request.json

    original_knowledge = get_knowledge_entry_from_db(knowledge_id)
    database = get_db()
    name = request.json["name"]
    chunk_size = request.json["chunk_size"]
    if request.json["embeddings"] != original_knowledge["embeddings"]:
        abort(
            make_response(
                jsonify(error="Cannot change the embeddings type afterwards."), 400
            )
        )
    database.execute(
        "UPDATE knowledge SET name = ?, chunk_size = ? WHERE id = ?",
        (name, chunk_size, knowledge_id),
    )
    database.commit()
    reset_global_knowledge(knowledge_id)
    return jsonify(
        {
            "id": knowledge_id,
            "name": name,
            "embeddings": original_knowledge["embeddings"],
            "chunk_size": chunk_size,
        }
    )


@bp.route("/<int:knowledge_id>", methods=["DELETE"])
@login_required
def delete_knowledge(knowledge_id):
    """Delete a knowledge entry."""
    persist_directory = get_knowledge_entry_from_db(knowledge_id)["persist_directory"]
    database = get_db()
    database.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
    database.commit()
    shutil.rmtree(persist_directory)
    reset_global_knowledge(knowledge_id)
    return ("", 204)


@bp.route("/<int:knowledge_id>/document/txt", methods=["POST"])
@login_required
def upload_txt(knowledge_id):
    """Add a txt file to a knowledge."""
    # pylint: disable=import-outside-toplevel
    from langchain.document_loaders import TextLoader

    file_path = handle_upload(request.files.get("file"))
    loader = TextLoader(file_path, encoding="utf8")
    load_into_knowledge(loader, knowledge_id)
    return ("", 204)


@bp.route("/<int:knowledge_id>/document/pdf", methods=["POST"])
@login_required
def upload_pdf(knowledge_id):
    """Add a pdf file to a knowledge."""
    # pylint: disable=import-outside-toplevel
    from langchain.document_loaders import PyPDFLoader

    file_path = handle_upload(request.files.get("file"))
    loader = PyPDFLoader(file_path)
    load_into_knowledge(loader, knowledge_id)
    return ("", 204)


@bp.route("/<int:knowledge_id>/document/docx", methods=["POST"])
@login_required
def upload_docx(knowledge_id):
    """Add a docx file to a knowledge."""
    # pylint: disable=import-outside-toplevel
    from langchain.document_loaders import Docx2txtLoader

    file_path = handle_upload(request.files.get("file"))
    loader = Docx2txtLoader(file_path)
    load_into_knowledge(loader, knowledge_id)
    return ("", 204)


def handle_upload(file):
    """Save the uploaded file to a temporary directory."""
    if not file:
        abort(make_response(jsonify(error="No file has been uploaded."), 400))
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)
    return file_path


def load_into_knowledge(loader: BaseLoader, knowledge_id: int):
    """Load content from the document loader into knowledge."""
    chunk_size = get_knowledge_entry_from_db(knowledge_id)["chunk_size"]
    chunks = loader.load_and_split(
        RecursiveCharacterTextSplitter(chunk_size=chunk_size)
    )
    add_to_knowledge(knowledge_id, chunks)
