from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import os

from .glovars import HOST, PORT, DEBUG
from . import database

app = Flask(__name__)
CORS(app, supports_credentials=True)

from . import error_handler
from . import routes

socketio = SocketIO(app, cors_allowed_origins="*")

from . import websocket


def app_run():
    socketio.run(
        app,
        host=HOST,
        port=PORT,
        debug=DEBUG,
        use_reloader=DEBUG,
        log_output=DEBUG,
        allow_unsafe_werkzeug=True
    )
