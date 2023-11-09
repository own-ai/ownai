"""Test access to the vector store."""
import pytest

from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.chroma import Chroma

from backaind.extensions import db
from backaind.knowledge import (
    add_knowledge,
    add_to_knowledge,
    get_embeddings,
    get_knowledge,
    KnowledgeConfigError,
)
import backaind.knowledge
from backaind.models import Knowledge


def test_get_embeddings_raises_on_unknown_embeddings(client):
    """Test if an exception is raised when requesting an unknown embedding function."""
    with client:
        client.get("/")
        with pytest.raises(KnowledgeConfigError) as error:
            get_embeddings("unknown")

        assert str(error.value) == "Unknown embeddings type: unknown"


def test_get_embeddings_returns_embeddings(client):
    """Test if get_embeddings() returns an Embeddings instance."""
    with client:
        client.get("/")
        embeddings = get_embeddings("huggingface")
        assert isinstance(embeddings, Embeddings)


def test_get_knowledge_returns_vector_store(client):
    """Test if get_knowledge() returns a VectorStore instance."""
    with client:
        client.get("/")
        knowledge = get_knowledge(1)
        assert isinstance(knowledge, VectorStore)


def test_get_knowledge_loads_from_global_knowledge():
    """Test if get_knowledge() loads from the global knowledge instance."""
    backaind.knowledge.global_knowledge = "NotRealKnowledge"
    backaind.knowledge.global_knowledge_id = 999
    knowledge = get_knowledge(999)
    assert knowledge == "NotRealKnowledge"


def test_add_to_knowledge_adds_documents(client):
    """Test if adding documents to knowledge works."""
    with client:
        client.get("/")
        add_to_knowledge(
            1, [Document(page_content="Test Document", metadata={"source": "Test"})]
        )
        knowledge = get_knowledge(1)
        result = knowledge.similarity_search("Test Document").pop()
        assert result.page_content == "Test Document"

        assert isinstance(knowledge, Chroma)
        # pylint: disable-next=protected-access
        knowledge._collection.delete(where_document={"$contains": "Test"})


def test_add_knowledge_command_adds_knowledge(app, runner):
    """Test if the add-knowledge command adds a new knowledge entry to the database."""
    knowledge_name = "Test"
    knowledge_embeddings = "huggingface"
    knowledge_chunk_size = "500"
    knowledge_persist_directory = "instance/knowledge-test"
    with app.app_context():
        knowledge_entry = (
            db.session.query(Knowledge).filter_by(name=knowledge_name).first()
        )
        assert knowledge_entry is None

        result = runner.invoke(
            add_knowledge,
            input=f"{knowledge_name}\n{knowledge_embeddings}\n{knowledge_chunk_size}\n"
            + f"{knowledge_persist_directory}",
        )
        assert f"Added {knowledge_name}" in result.output

        knowledge_entry = (
            db.session.query(Knowledge).filter_by(name=knowledge_name).first()
        )
        assert knowledge_entry is not None


def test_add_knowledge_command_updates_knowledge(app, runner):
    """Test if the add-knowledge command updates knowledge with the same name."""
    knowledge_name = "Test 1"
    knowledge_embeddings = "huggingface"
    knowledge_chunk_size = "500"
    knowledge_persist_directory = "instance/knowledge"
    with app.app_context():
        knowledge_entry = (
            db.session.query(Knowledge).filter_by(name=knowledge_name).one()
        )
        knowledge_entry.persist_directory = "old_directory"
        db.session.commit()

        result = runner.invoke(
            add_knowledge,
            input=f"{knowledge_name}\n{knowledge_embeddings}\n{knowledge_chunk_size}\n"
            + f"{knowledge_persist_directory}",
        )
        assert f"Updated {knowledge_name}" in result.output

        knowledge_entry = (
            db.session.query(Knowledge).filter_by(name=knowledge_name).one()
        )
        assert knowledge_entry.persist_directory == knowledge_persist_directory
