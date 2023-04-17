"""Backaind is the ownAI Flask application to manage and run your own AI models."""
import os

from flask import Flask, g
from flask_socketio import SocketIO
from . import ainteraction, auth, db

socketio = SocketIO()

def create_app(test_config=None):
    """Create a new ownAI Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'ownAI.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.before_request(register_vite_dev_server)
    socketio.init_app(app)
    db.init_app(app)
    auth.init_app(app)
    ainteraction.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(ainteraction.bp)
    app.add_url_rule('/', endpoint='index')

    return app

def register_vite_dev_server():
    """Make Vite port available if Vite dev server should be used."""
    g.vite_dev_server_enabled = 'VITE_PORT' in os.environ
    g.vite_dev_server_port = os.environ.get('VITE_PORT')
