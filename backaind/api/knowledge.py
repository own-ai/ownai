"""API to create, read, update and delete knowledge."""
import os
import shutil
import tempfile
import uuid

from flask import Blueprint, jsonify, request, make_response, abort, current_app
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..auth import login_required
from ..extensions import db
from ..knowledge import (
    add_to_knowledge,
    reset_global_knowledge,
    get_from_knowledge,
    delete_from_knowledge,
)
from ..models import Knowledge

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
    return [knowledge.as_dict() for knowledge in db.session.query(Knowledge).all()]


@bp.route("/<int:knowledge_id>", methods=["GET"])
@login_required
def get_knowledge(knowledge_id):
    """Get a specific knowledge entry."""
    knowledge = db.get_or_404(Knowledge, knowledge_id)
    return knowledge.as_dict()


@bp.route("/", methods=["POST"])
@login_required
def create_knowledge():
    """Create a new knowledge entry."""
    validate(request.json)
    assert request.json

    name = request.json["name"]
    embeddings = request.json["embeddings"]
    chunk_size = request.json["chunk_size"]
    persist_directory = os.path.join(
        current_app.instance_path, "knowledge-" + uuid.uuid4().hex
    )
    os.makedirs(persist_directory)

    new_knowledge = Knowledge(
        name=name,
        embeddings=embeddings,
        chunk_size=chunk_size,
        persist_directory=persist_directory,
    )
    db.session.add(new_knowledge)
    db.session.commit()
    return (
        jsonify(new_knowledge.as_dict()),
        201,
    )


@bp.route("/<int:knowledge_id>", methods=["PUT"])
@login_required
def update_knowledge(knowledge_id):
    """Update a knowledge entry."""
    validate(request.json)
    assert request.json

    existing_knowledge = db.get_or_404(Knowledge, knowledge_id)
    name = request.json["name"]
    chunk_size = request.json["chunk_size"]
    if request.json["embeddings"] != existing_knowledge.embeddings:
        abort(
            make_response(
                jsonify(error="Cannot change the embeddings type afterwards."), 400
            )
        )

    existing_knowledge.name = name
    existing_knowledge.chunk_size = chunk_size
    db.session.commit()
    reset_global_knowledge(knowledge_id)
    return jsonify(
        {
            "id": knowledge_id,
            "name": name,
            "embeddings": existing_knowledge.embeddings,
            "chunk_size": chunk_size,
        }
    )


@bp.route("/<int:knowledge_id>", methods=["DELETE"])
@login_required
def delete_knowledge(knowledge_id):
    """Delete a knowledge entry."""
    existing_knowledge = db.get_or_404(Knowledge, knowledge_id)
    persist_directory = existing_knowledge.persist_directory
    db.session.delete(existing_knowledge)
    db.session.commit()
    shutil.rmtree(persist_directory)
    reset_global_knowledge(knowledge_id)
    return ("", 204)


@bp.route("/<int:knowledge_id>/document", methods=["GET"])
@login_required
def get_documents(knowledge_id):
    """Get documents from the specific knowledge."""
    limit = request.args.get("limit", 10, type=int)
    offset = request.args.get("offset", 0, type=int)
    return get_from_knowledge(knowledge_id, limit, offset)


@bp.route("/<int:knowledge_id>/document/<string:document_id>", methods=["DELETE"])
@login_required
def delete_document(knowledge_id, document_id):
    """Delete a document from a knowledge."""
    delete_from_knowledge(knowledge_id, [document_id])
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
    knowledge = db.get_or_404(Knowledge, knowledge_id)
    chunks = loader.load_and_split(
        RecursiveCharacterTextSplitter(chunk_size=knowledge.chunk_size)
    )
    add_to_knowledge(knowledge_id, chunks)
