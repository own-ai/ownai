"""Define test configuration and fixtures."""
import json

import pytest

from backaind import create_app
from backaind.extensions import db
from backaind.models import User, Ai, Knowledge


@pytest.fixture(name="app")
def fixture_app():
    """Factory function for the Flask server app fixture."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///testing.db",
            "SECRET_KEY": "Only4Testing",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_test_data()

    yield app


@pytest.fixture(name="client")
def fixture_client(app):
    """Factory function for the test client fixture."""
    return app.test_client()


@pytest.fixture(name="runner")
def fixture_runner(app):
    """Factory function for the click CLI runner."""
    return app.test_cli_runner()


class AuthActions:
    """Helper class for authentication actions in tests."""

    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        """Perform a login."""
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        """Perform a logout."""
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    """Factory function for authentication actions."""
    return AuthActions(client)


def insert_test_data():
    """Insert test data into the database."""
    db.session.add(
        User(
            username="test",
            passhash="pbkdf2:sha256:"
            + "50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f",
        )
    )
    db.session.add(
        User(
            username="other",
            passhash="pbkdf2:sha256:"
            + "50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79",
        )
    )

    db.session.add(
        Ai(
            name="OpenAssistant SFT-4 12B @HuggingFace-Hub",
            input_keys=["input_text"],
            chain=json.loads(
                """{
                    "memory": null,
                    "verbose": false,
                    "prompt": {
                        "input_variables": ["input_text"],
                        "output_parser": null,
                        "partial_variables": {},
                        "template": "<|prompter|>{input_text}<|endoftext|><|assistant|>",
                        "template_format": "f-string",
                        "validate_template": true,
                        "_type": "prompt"
                    },
                    "llm": {
                        "repo_id": "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
                        "task": null,
                        "model_kwargs": {"max_new_tokens": 200},
                        "_type": "huggingface_hub"
                    },
                    "output_key": "output_text",
                    "_type": "llm_chain"
                }"""
            ),
            is_public=True,
        )
    )
    db.session.add(
        Ai(
            name="OpenAssistant SFT-4 12B with knowledge @HuggingFace-Hub",
            input_keys=["input_text", "input_knowledge"],
            chain=json.loads(
                # pylint: disable=line-too-long
                """{
                    "memory": null,
                    "callbacks": null,
                    "callback_manager": null,
                    "verbose": false,
                    "input_key": "input_knowledge",
                    "output_key": "output_text",
                    "llm_chain": {
                        "memory": null,
                        "callbacks": null,
                        "callback_manager": null,
                        "verbose": false,
                        "prompt": {
                            "input_variables": ["summaries", "input_text"],
                            "output_parser": null,
                            "partial_variables": {},
                            "template": "<|prompter|>Please answer this question: {input_text}\\nUse the following information:\\n{summaries}\\n<|endoftext|><|assistant|>",
                            "template_format": "f-string",
                            "validate_template": true, "_type": "prompt"
                        },
                        "llm": {
                            "repo_id": "OpenAssistant/oasst-sft-4-pythia-12b-epoch-3.5",
                            "task": null,
                            "model_kwargs": {"max_new_tokens": 200},
                            "_type": "huggingface_hub"
                        },
                        "output_key": "text",
                        "_type": "llm_chain"
                    },
                    "document_prompt": {
                        "input_variables": ["page_content", "source"],
                        "output_parser": null,
                        "partial_variables": {},
                        "template": "Context: {page_content}\\nSource: {source}",
                        "template_format": "f-string",
                        "validate_template": true,
                        "_type": "prompt"
                    },
                    "document_variable_name": "summaries",
                    "document_separator": "\\n\\n",
                    "_type": "stuff_documents_chain"
                }"""
                # pylint: enable=line-too-long
            ),
        )
    )

    db.session.add(
        Knowledge(
            name="Test 1",
            embeddings="huggingface",
            chunk_size=500,
            persist_directory="instance/test-knowledge-1",
            is_public=True,
        )
    )
    db.session.add(
        Knowledge(
            name="Test 2",
            embeddings="huggingface",
            chunk_size=500,
            persist_directory="instance/test-knowledge-2",
        )
    )

    db.session.commit()
