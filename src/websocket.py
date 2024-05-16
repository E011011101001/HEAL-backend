from datetime import datetime

from flask import request
from flask_socketio import emit, disconnect

from . import socketio
from . import database as db

@socketio.on('connect')
def connect():
    print(f'New client connected: {request.sid}')

@socketio.on('disconnect')
def disconnect():
    print(f'Client disconnected: {request.sid}')

@socketio.on('auth')
def auth(json):
    token = json.get('token')
    roomId = json.get('roomId')

    try:
        user = db.user.get_user_by_token(token)
    except Exception:
        user = None
    finally:
        if user is None or user['expirationTime'] < datetime.now():
            emit('auth', {
                'error': 'Forbidden'
            })

    emit('auth', user)

