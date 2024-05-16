from functools import wraps
from datetime import datetime

from flask import request
from flask_socketio import emit, disconnect

from . import socketio
from . import database as db


wsSessions = []

@socketio.on('connect')
def connect(auth):
    token = auth.get('token')
    roomId = auth.get('roomId')
    sid = request.sid

    try:
        user = db.user.get_user_by_token(token)
    except Exception:
        user = None
    finally:
        if user is None or user['expirationTime'] < datetime.now():
            disconnect()

    wsSessions.append({
        'user': user,
        'roomId': roomId,
        'sid': sid
    })


@socketio.on('disconnect')
def on_disconnect():
    print(f'Client disconnected: {request.sid}')

