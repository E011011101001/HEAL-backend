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
def message(session, json):
    """
    1. Get room stage.
    2. If there is no active doctor in the room, stage = 1, and message sent to chatbot;
    3. If there is at least one active doctor in the room, stage = 2, and message sent to socketio room.
    4. If the other user in the room speaks a different language, send translation along with the message.

    For all the messages sending to the front end:
    1. Get terms by GPT.
    2. If terms exists in the database, send the data stored in the database.
    3. If terms does not exist, ask GPT for information and possible wiki links of the term. Send the data, and
        store them in the database.
    4. After 2&3, store the terms in the chat history

    """
