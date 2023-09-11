"""Backaind is the ownAI Flask application to manage and run your own AI models."""
import os

from flask import Flask, g

from . import aifile, ainteraction, auth, knowledge, settings, workshop
from .api import ai as api_ai, knowledge as api_knowledge
from .extensions import db, migrate, socketio
from .models import *


def create_app(test_config=None):
    """Create a new ownAI Flask application."""
    app = Flask(__name__)

    if test_config is None:
        # load from environment when not testing
        app.config.from_prefixed_env("OWNAI")
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # init extensions and blueprints
    app.before_request(register_vite_dev_server)
    socketio.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    auth.init_app(app)
    aifile.init_app(app)
    ainteraction.init_app(app)
    knowledge.init_app(app)

    # register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(ainteraction.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(workshop.bp)
    app.register_blueprint(api_ai.bp)
    app.register_blueprint(api_knowledge.bp)
    app.add_url_rule("/", endpoint="index")

    return app


def register_vite_dev_server():
    """Make Vite port available if Vite dev server should be used."""
    g.vite_dev_server_enabled = "VITE_PORT" in os.environ
    g.vite_dev_server_port = os.environ.get("VITE_PORT")
