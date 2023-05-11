"""Test access to the vector store."""
import tempfile
import shutil
from flask import current_app, session
import pytest
from langchain.embeddings.base import Embeddings
from langchain.vectorstores.base import VectorStore
from backaind.knowledge import get_embedding_function, get_knowledge, KnowledgeConfigError

def test_get_embedding_function_raises_on_unknown_embeddings(client):
    """Test if an exception is raised when requesting an unknown embedding function."""
    with client:
        client.get('/')
        current_app.config['KNOWLEDGE_EMBEDDINGS'] = 'unknown'
        with pytest.raises(KnowledgeConfigError) as error:
            get_embedding_function()

        assert str(error.value) == 'Unknown embeddings type: unknown'

def test_get_embedding_function_returns_embeddings(client):
    """Test if get_embedding_function() returns an Embeddings instance."""
    with client:
        client.get('/')
        current_app.config['KNOWLEDGE_EMBEDDINGS'] = 'huggingface'
        embeddings = get_embedding_function()
        assert isinstance(embeddings, Embeddings)

def test_get_knowledge_raises_when_persist_directory_not_set(client):
    """Test if an exception is raised when no knowledge persist directory is set."""
    with client:
        client.get('/')
        with pytest.raises(KnowledgeConfigError) as error:
            get_knowledge()

        assert str(error.value) == 'Knowledge persist directory is not set.'

def test_get_knowledge_returns_vector_store(client):
    """Test if get_knowledge() returns a VectorStore instance."""
    knowledge_path = tempfile.mkdtemp()
    with client:
        client.get('/')
        current_app.config['KNOWLEDGE_EMBEDDINGS'] = 'huggingface'
        current_app.config['KNOWLEDGE_PERSIST_DIRECTORY'] = knowledge_path
        knowledge = get_knowledge()
        assert isinstance(knowledge, VectorStore)
    shutil.rmtree(knowledge_path)

def test_get_knowledge_returns_from_session(client):
    """Test if get_knowledge() caches the instance in session."""
    with client:
        client.get('/')
        session['knowledge'] = 'NotRealKnowledge'
        knowledge = get_knowledge()
        assert knowledge == 'NotRealKnowledge'
