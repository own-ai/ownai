"""
    Provide vector store capabilities to save and access 'knowledge'.
    Currently only Chroma is supported as vector store.
"""
from typing import List
from threading import Lock
import uuid

import click
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.chroma import Chroma

from .extensions import db
from .models import Knowledge

# pylint: disable=invalid-name
global_knowledge = None
global_knowledge_id = None
# pylint: enable=invalid-name
knowledge_lock = Lock()


class KnowledgeConfigError(Exception):
    """Invalid or missing knowledge configuration."""


def get_embeddings(embeddings_type: str) -> Embeddings:
    """Return an Embeddings instance for the given embeddings_type."""
    if embeddings_type.lower() == "huggingface":
        # pylint: disable=import-outside-toplevel
        from langchain.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings()

    raise KnowledgeConfigError(f"Unknown embeddings type: {embeddings_type}")


def get_knowledge(knowledge_id: int) -> VectorStore:
    """Return a vector store instance to be used for knowledge access."""
    # pylint: disable=global-statement
    global global_knowledge, global_knowledge_id
    with knowledge_lock:
        knowledge = global_knowledge
        if not knowledge or global_knowledge_id != knowledge_id:
            knowledge_entry = db.get_or_404(Knowledge, knowledge_id)
            knowledge = Chroma(
                persist_directory=knowledge_entry.persist_directory,
                embedding_function=get_embeddings(knowledge_entry.embeddings),
            )
            global_knowledge = knowledge
            global_knowledge_id = knowledge_id
    return knowledge


def reset_global_knowledge(knowledge_id=None):
    """
    Drop the global knowledge instance.
    If knowledge_id is set, it only drops the global knowledge instance if it matches this ID.
    """
    # pylint: disable=global-statement
    global global_knowledge, global_knowledge_id
    with knowledge_lock:
        if not knowledge_id or knowledge_id == global_knowledge_id:
            global_knowledge = None
            global_knowledge_id = None


def add_to_knowledge(knowledge_id: int, documents: List[Document]):
    """Add documents to the specified knowledge."""
    knowledge = get_knowledge(knowledge_id)
    knowledge.add_documents(
        documents, ids=[str(uuid.uuid4()) for _ in range(len(documents))]
    )


def get_from_knowledge(knowledge_id: int, limit: int, offset: int):
    """Get documents from the specified knowledge."""
    knowledge = get_knowledge(knowledge_id)
    assert isinstance(
        knowledge, Chroma
    ), "Can only get documents from Chroma vector stores."
    total = knowledge._collection.count()  # pylint: disable=protected-access
    collection = knowledge.get(limit=limit, offset=offset)
    return {
        "total": total,
        "items": [
            {"id": id, "text": text}
            for id, text in zip(collection["ids"], collection["documents"])
        ],
    }


def delete_from_knowledge(knowledge_id: int, document_ids: List[str]):
    """Delete documents from the specified knowledge."""
    knowledge = get_knowledge(knowledge_id)
    knowledge.delete(document_ids)


@click.command("add-knowledge")
@click.option("--name", prompt="Name")
@click.option(
    "--embeddings",
    prompt="Embeddings",
    type=click.Choice(["huggingface"], case_sensitive=False),
)
@click.option("--chunk-size", prompt="Chunk size in characters", type=int, default=500)
@click.option(
    "--persist-directory", prompt="Directory to persist the knowledge database"
)
def add_knowledge(name, embeddings, chunk_size, persist_directory):
    """Register a new knowledge store or update a knowledge store with the same name."""
    embeddings = embeddings.lower()
    existing_knowledge = db.session.query(Knowledge).filter_by(name=name).first()

    if existing_knowledge is None:
        new_knowledge = Knowledge(
            name=name,
            embeddings=embeddings,
            chunk_size=chunk_size,
            persist_directory=persist_directory,
        )
        db.session.add(new_knowledge)
        db.session.commit()
        click.echo(f"Added {name}. Thank you for making me smarter!")
    else:
        existing_knowledge.embeddings = embeddings
        existing_knowledge.chunk_size = chunk_size
        existing_knowledge.persist_directory = persist_directory
        existing_knowledge.name = name
        db.session.commit()
        reset_global_knowledge()
        click.echo(f"Updated {name}. Thank you for making me smarter!")


def init_app(app):
    """Register CLI commands with the application instance."""
    app.cli.add_command(add_knowledge)
