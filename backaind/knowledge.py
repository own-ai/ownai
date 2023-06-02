"""
    Provide vector store capabilities to save and access 'knowledge'.
    Currently only Chroma is supported as vector store.
"""
from typing import List
import click
from flask import session
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores import Chroma
from backaind.db import get_db


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
    knowledge = session.get(f"knowledge[{knowledge_id}]")
    if not knowledge:
        knowledge_entry = get_knowledge_entry_from_db(knowledge_id)
        knowledge = Chroma(
            persist_directory=knowledge_entry["persist_directory"],
            embedding_function=get_embeddings(knowledge_entry["embeddings"]),
        )
        session[f"knowledge[{knowledge_id}]"] = knowledge
    return knowledge


def add_to_knowledge(knowledge_id: int, documents: List[Document]):
    """Add documents to the specified knowledge."""
    knowledge_entry = get_knowledge_entry_from_db(knowledge_id)
    knowledge = Chroma(
        persist_directory=knowledge_entry["persist_directory"],
        embedding_function=get_embeddings(knowledge_entry["embeddings"]),
    )
    knowledge.add_documents(documents)
    knowledge.persist()


def get_knowledge_entry_from_db(knowledge_id: int):
    """Return a specific knowledge entry from the database."""
    database = get_db()
    knowledge_entry = database.execute(
        "SELECT * FROM knowledge WHERE id = ?", (knowledge_id,)
    ).fetchone()
    return knowledge_entry


def get_all_knowledge_entries_from_db():
    """Return all knowledge entries from the database."""
    database = get_db()
    knowledge_entries = database.execute("SELECT * FROM knowledge").fetchall()
    return knowledge_entries


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
    database = get_db()

    existing_knowledge = database.execute(
        "SELECT * FROM knowledge WHERE name = ?", (name,)
    ).fetchone()

    if existing_knowledge is None:
        database.execute(
            """
            INSERT INTO knowledge (name, embeddings, chunk_size, persist_directory)
            VALUES (?, ?, ?, ?)
            """,
            (name, embeddings, chunk_size, persist_directory),
        )
        database.commit()
        click.echo(f"Added {name}. Thank you for making me smarter!")
    else:
        database.execute(
            """
            UPDATE knowledge
            SET embeddings = ?, chunk_size = ?, persist_directory = ?
            WHERE name = ?
            """,
            (embeddings, chunk_size, persist_directory, name),
        )
        database.commit()
        click.echo(f"Updated {name}. Thank you for making me smarter!")


def init_app(app):
    """Register CLI commands with the application instance."""
    app.cli.add_command(add_knowledge)
