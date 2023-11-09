"""Test the Knowledge API."""
import os
import json
import shutil

from langchain.vectorstores.chroma import Chroma
import pytest

from backaind.extensions import db
from backaind.knowledge import get_knowledge
from backaind.models import Knowledge


def test_auth_required(client):
    """Test whether authorization is required to access the API."""
    assert client.get("/api/knowledge/").status_code == 401
    assert client.get("/api/knowledge/2").status_code == 401
    assert client.post("/api/knowledge/", json={}).status_code == 401
    assert client.post("/api/knowledge/1/document/txt", data={}).status_code == 401
    assert client.post("/api/knowledge/1/document/pdf", data={}).status_code == 401
    assert client.post("/api/knowledge/1/document/docx", data={}).status_code == 401
    assert client.put("/api/knowledge/1", json={}).status_code == 401
    assert client.delete("/api/knowledge/1").status_code == 401
    assert client.get("/api/knowledge/1/document").status_code == 401
    assert client.delete("/api/knowledge/1/document/test").status_code == 401


def test_get_all_knowledge(client, auth):
    """Test if GET /api/knowledge/ returns all knowledge from the database."""
    auth.login()
    response = client.get("/api/knowledge/")
    assert 2 == len(json.loads(response.data))


def test_get_knowledge(client, auth):
    """Test if GET /api/knowledge/1 returns the knowledge entry with id 1."""
    auth.login()
    response = client.get("/api/knowledge/1")
    assert 1 == json.loads(response.data)["id"]


def test_get_unknown_knowledge_returns_404(client, auth):
    """Test if GET /api/knowledge/999 returns 404."""
    auth.login()
    response = client.get("/api/knowledge/999")
    assert response.status_code == 404


def test_create_knowledge(client, auth, app):
    """Test if POST /api/knowledge/ creates a new knowledge entry."""
    auth.login()
    response = client.post(
        "/api/knowledge/",
        json={"name": "Test", "embeddings": "huggingface", "chunk_size": 500},
    )
    assert json.loads(response.data)["id"] == 3
    with app.app_context():
        entry = db.get_or_404(Knowledge, 3)
        assert entry and entry.name == "Test"
        shutil.rmtree(entry.persist_directory)


def test_update_knowledge(client, auth, app):
    """Test if PUT /api/knowledge/1 updates the entry."""
    auth.login()
    response = client.put(
        "/api/knowledge/1",
        json={"name": "Test", "embeddings": "huggingface", "chunk_size": 500},
    )
    assert json.loads(response.data)["name"] == "Test"
    with app.app_context():
        entry = db.get_or_404(Knowledge, 1)
        assert entry and entry.name == "Test"


def test_update_knowledge_does_not_update_embeddings(client, auth, app):
    """Test if the embeddings type cannot be updated afterwards."""
    with app.app_context():
        knowledge = db.session.get(Knowledge, 1)
        assert knowledge
        knowledge.embeddings = "changed"
        db.session.commit()

        auth.login()
        response = client.put(
            "/api/knowledge/1",
            json={"name": "Test", "embeddings": "huggingface", "chunk_size": 500},
        )
        assert response.status_code == 400
        assert (
            json.loads(response.data)["error"]
            == "Cannot change the embeddings type afterwards."
        )


def test_delete_knowledge(client, auth, app):
    """Test if DELETE /api/knowledge/1 deletes the entry."""
    os.makedirs("instance/test-knowledge-2")
    auth.login()
    response = client.delete("/api/knowledge/2")
    assert response.status_code == 204
    with app.app_context():
        entry = db.session.get(Knowledge, 2)
        assert entry is None


def test_get_documents(client, auth):
    """Test if GET /api/knowledge/1/document returns all documents from the knowledge."""
    with client, open("tests/test_documents/test.txt", "rb") as file:
        auth.login()
        client.post(
            "/api/knowledge/1/document/txt",
            data={"file": (file, "test.txt")},
            buffered=True,
            content_type="multipart/form-data",
        )
        response = client.get("/api/knowledge/1/document")
        assert 1 == len(json.loads(response.data)["items"])

        knowledge = get_knowledge(1)
        assert isinstance(knowledge, Chroma)
        # pylint: disable-next=protected-access
        knowledge._collection.delete(where_document={"$contains": "test"})


def test_delete_document(client, auth):
    """Test if DELETE /api/knowledge/1/document/<id> deletes the document."""
    with client, open("tests/test_documents/test.txt", "rb") as file:
        auth.login()
        client.post(
            "/api/knowledge/1/document/txt",
            data={"file": (file, "test.txt")},
            buffered=True,
            content_type="multipart/form-data",
        )
        response = client.get("/api/knowledge/1/document")
        document_id = json.loads(response.data)["items"][0]["id"]
        response = client.delete("/api/knowledge/1/document/" + document_id)
        assert response.status_code == 204
        response = client.get("/api/knowledge/1/document")
        assert 0 == len(json.loads(response.data)["items"])

        knowledge = get_knowledge(1)
        assert isinstance(knowledge, Chroma)
        # pylint: disable-next=protected-access
        knowledge._collection.delete(where_document={"$contains": "test"})


def test_upload_txt(client, auth):
    """Test uploading a txt document into knowledge."""
    with client, open("tests/test_documents/test.txt", "rb") as file:
        auth.login()
        client.post(
            "/api/knowledge/1/document/txt",
            data={"file": (file, "test.txt")},
            buffered=True,
            content_type="multipart/form-data",
        )
        knowledge = get_knowledge(1)
        results = knowledge.similarity_search("txt")
        assert results.pop().page_content == "This is a txt test file."

        assert isinstance(knowledge, Chroma)
        # pylint: disable-next=protected-access
        knowledge._collection.delete(where_document={"$contains": "test"})


def test_upload_pdf(client, auth):
    """Test uploading a pdf document into knowledge."""
    with client, open("tests/test_documents/test.pdf", "rb") as file:
        auth.login()
        client.post(
            "/api/knowledge/1/document/pdf",
            data={"file": (file, "test.pdf")},
            buffered=True,
            content_type="multipart/form-data",
        )
        knowledge = get_knowledge(1)
        results = knowledge.similarity_search("pdf")
        assert results.pop().page_content == "This is a pdf test file."

        assert isinstance(knowledge, Chroma)
        # pylint: disable-next=protected-access
        knowledge._collection.delete(where_document={"$contains": "test"})


def test_upload_docx(client, auth):
    """Test uploading a docx document into knowledge."""
    with client, open("tests/test_documents/test.docx", "rb") as file:
        auth.login()
        client.post(
            "/api/knowledge/1/document/docx",
            data={"file": (file, "test.docx")},
            buffered=True,
            content_type="multipart/form-data",
        )
        knowledge = get_knowledge(1)
        results = knowledge.similarity_search("docx")
        assert results.pop().page_content == "This is a docx test file."

        assert isinstance(knowledge, Chroma)
        # pylint: disable-next=protected-access
        knowledge._collection.delete(where_document={"$contains": "test"})


def test_upload_no_file_fails(client, auth):
    """Test if uploading no file fails."""
    with client:
        auth.login()
        response = client.post(
            "/api/knowledge/1/document/pdf",
            data={},
            buffered=True,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        assert json.loads(response.data)["error"] == "No file has been uploaded."


@pytest.mark.parametrize(
    "data,message",
    (
        (
            {},
            "The knowledge data cannot be empty.",
        ),
        (
            {"embeddings": "huggingface", "chunk_size": 500},
            'The property "name" is required.',
        ),
        (
            {"name": 1, "embeddings": "huggingface", "chunk_size": 500},
            'The property "name" has to be a string.',
        ),
        (
            {"name": "Test", "chunk_size": 500},
            'The property "embeddings" is required.',
        ),
        (
            {"name": "Test", "embeddings": "doesnotexist", "chunk_size": 500},
            "Unknown embeddings type.",
        ),
        (
            {"name": "Test", "embeddings": "huggingface"},
            'The property "chunk_size" is required.',
        ),
        (
            {"name": "Test", "embeddings": "huggingface", "chunk_size": "Test"},
            'The property "chunk_size" has to be a number.',
        ),
    ),
)
def test_validation(client, auth, data, message):
    """Test if the knowledge JSON validation works."""
    auth.login()
    response = client.put("/api/knowledge/1", json=data)
    assert response.status_code == 400
    assert json.loads(response.data)["error"] == message
