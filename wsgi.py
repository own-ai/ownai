#!/bin/env python
"""ownAI WSGI entry point"""
from backaind import create_app
from backaind.extensions import socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app)
