"""SQLAlchemy models"""
from .extensions import db


class User(db.Model):
    """User model"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    passhash = db.Column(db.String, nullable=False)

    settings = db.relationship(
        "Setting", backref="user", lazy=True, cascade="all, delete-orphan"
    )


class Ai(db.Model):
    """Ai model"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    input_keys = db.Column(db.JSON, nullable=False)
    input_labels = db.Column(db.JSON, nullable=True)
    chain = db.Column(db.JSON, nullable=False)
    greeting = db.Column(db.String, nullable=True)
    is_public = db.Column(db.Boolean, nullable=False, default=False)

    def as_dict(self):
        """Return the model as a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "input_keys": self.input_keys,
            "input_labels": self.input_labels,
            "chain": self.chain,
            "greeting": self.greeting,
        }


class Knowledge(db.Model):
    """Knowledge model"""

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    embeddings = db.Column(db.String, nullable=False)
    chunk_size = db.Column(db.Integer, nullable=False)
    persist_directory = db.Column(db.String, nullable=False)
    is_public = db.Column(db.Boolean, nullable=False, default=False)

    def as_dict(self):
        """Return the model as a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "embeddings": self.embeddings,
            "chunk_size": self.chunk_size,
            # persist_directory is internal
        }


class Setting(db.Model):
    """Setting model"""

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    domain = db.Column(db.String, primary_key=True, nullable=False)
    name = db.Column(db.String, primary_key=True, nullable=False)
    value = db.Column(db.String, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "domain", "name", name="settings_user_domain_name"
        ),
    )
