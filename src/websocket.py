# src/websocket.py
from functools import wraps
from datetime import datetime
from peewee import DoesNotExist

from flask import request
from flask_socketio import emit, disconnect

from . import socketio
from . import database as db


wsSessions = []


def get_session(func):
    @wraps(func)
    def inner(*args, **kwargs):
        global wsSessions
        # get session from wsSession by session[sid]
        sid = request.sid
        try:
            session = list(filter(lambda session : session['sid'] == sid, wsSessions))[0]
        except IndexError:
            emit ('error', {
                'error': 'InternalServerError',
                'message': 'User is authenticated. However, no registered sid is found.'
            })
            disconnect()
            return

        return func(session, *args, **kwargs)

    return inner


@socketio.on('connect')
def connect(auth):
    token = auth.get('token')
    roomId = auth.get('roomId')
    sid: str = request.sid

    unauthError = {
        'error': 'unauthorizationError'
    }

    # Check if logged in
    try:
        user = db.user.get_user_by_token(token)
        if user and user['expirationTime'] < datetime.now():
            user = None
    except DoesNotExist:
        user = None

    if user is None:
        unauthError['message'] = 'User invalid'
        emit('error', unauthError)
        disconnect()
        return

    # Check if in room
    try:
        rooms = db.room_op.get_rooms_all(user['id'])['rooms']
        roomIds = list(map(lambda room: room.get('roomId'), rooms))

    except DoesNotExist:
        roomIds = []

    if roomId not in roomIds:
        unauthError['message'] = 'Room invalid'
        emit('error', unauthError)
        disconnect()
        return

    wsSessions.append({
        'user': user,
        'roomId': roomId,
        'sid': sid
    })


@socketio.on('disconnect')
def on_disconnect():
    print(f'User disconnected: {request.sid}')
    global wsSessions
    wsSessions = [session for session in wsSessions if session['sid'] != request.sid]


@socketio.on('message')
@get_session
def message(data):
    pass
