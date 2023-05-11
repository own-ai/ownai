"""
    Provide vector store capabilities to save and access 'knowledge'.
    Currently only Chroma is supported as vector store.
"""
from flask import current_app, session
from langchain.vectorstores import Chroma


class KnowledgeConfigError(Exception):
    """Invalid or missing knowledge configuration."""


def get_embedding_function():
    """Return the embedding function according to the configuration."""
    embeddings_type = current_app.config.get("KNOWLEDGE_EMBEDDINGS", "")
    if embeddings_type.lower() == "huggingface":
        # pylint: disable=import-outside-toplevel
        from langchain.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings()

    raise KnowledgeConfigError(f"Unknown embeddings type: {embeddings_type}")


def get_knowledge():
    """Return a vector store instance to be used for knowledge access."""
    knowledge = session.get("knowledge")
    if not knowledge:
        persist_directory = current_app.config.get("KNOWLEDGE_PERSIST_DIRECTORY", None)
        if not persist_directory:
            raise KnowledgeConfigError("Knowledge persist directory is not set.")
        knowledge = Chroma(
            persist_directory=persist_directory,
            embedding_function=get_embedding_function(),
        )
        session["knowledge"] = knowledge
    return knowledge
