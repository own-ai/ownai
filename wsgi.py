#!/bin/env python
"""ownAI WSGI entry point"""
from backaind import create_app, socketio

app = create_app()

if __name__ == "__main__":
    socketio.run(app)
