"""Make extensions available in all modules."""
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

socketio = SocketIO()
db = SQLAlchemy()
migrate = Migrate()
