# src/websocket.py
from datetime import datetime

from flask import request
from flask_socketio import emit, disconnect, join_room

from . import socketio
from . import database as db


"""
wsSession = [{
    'user': db.user.get_user_full(user_id),
    'roomId': roomId,
    'sid': sid
}]
"""
wsSessions = []

"""
chatBots = {
    3: <ChatBot>,
    16: <ChatBot>,
    ...
}
"""
chatBots = {}


def get_session() -> dict:
    global wsSessions
    # get session from wsSession by session[sid]
    sid = request.sid  # type: ignore
    try:
        return list(filter(lambda session : session['sid'] == sid, wsSessions))[0]
    except IndexError:
        emit('error', {
            'error': 'InternalServerError',
            'message': 'User is authenticated. However, no registered sid is found.'
        })
        disconnect()
        raise


@socketio.on('connect')
def connect(auth: dict):
    token = auth.get('token')
    roomId = auth.get('roomId')
    sid: str = request.sid # type: ignore

    unauthError = {
        'error': 'unauthorizationError'
    }

    # Check if logged in
    session = db.user.get_session_by_token(token)
    if session and session['expirationTime'] < datetime.now():
        session = None

    if session is None:
        unauthError['message'] = 'User invalid'
        emit('error', unauthError)
        disconnect()
        return

    # Check if in room
    rooms = db.room_op.get_rooms_all(session['userId'])['rooms']
    roomIds = list(map(lambda room: room.get('roomId'), rooms))

    if roomId not in roomIds:
        unauthError['message'] = 'Room invalid'
        emit('error', unauthError)
        disconnect()
        return

    # Add user to SocketIO room of roomId
    join_room(roomId)

    wsSessions.append({
        'user': db.user.get_user_full(session['userId']),
        'roomId': roomId,
        'sid': sid
    })


@socketio.on('disconnect')
def on_disconnect():
    global wsSessions

    session = get_session()
    print(f"User disconnected:\n"
        f"    User ID: {session['user']['id']};"
        f"    User Name: {session['user']['name']}.")

    # leaving rooms is done by the framework
    wsSessions.remove(session)


def make_message(text: str, translation: str | None) -> dict:
    """
    For all the messages sending to the front end:
    1. Get terms by GPT.
    2. If terms exists in the database, send the data stored in the database.
    3. If terms does not exist, ask GPT for information and possible wiki links of the term. Send the data, and
        store them in the database.
    4. After 2&3, store the terms in the chat history
    """
    pass


def save_client_message(session: dict, text: str, time_iso_format: str) -> None:
    db.message_op.save_message_only(
        session['user']['id'],
        session['roomId'],
        text,
        datetime.fromisoformat(time_iso_format)
    )


@socketio.on('message')
def message(json: dict):
    """
    1. Get room stage.
    2. If there is no active doctor in the room, stage = 1, and message sent to chatbot;
    3. If there is at least one active doctor in the room, stage = 2, and message sent to socketio room.
    4. If the other user in the room speaks a different language, send translation along with the message.

    """

    global chatBots
    session = get_session()

    if json.get('text') is None or json.get('timestamp') is None:
        emit('error', {
            'error': 'missing items',
            'message': '"message" and "timestamp" are required'
        })
        return

    save_client_message(session, json['text'], json['timestamp'].split('Z')[0])

    roomId = session['roomId']
    doctors = db.room_op.get_room_doctor_ids(roomId)
    if len(doctors) == 0:
        # stage == 1
        if chatBots.get(roomId) is None:
            # TODO: implement chat bot
            chatBots[roomId] = ChatBot(lan=session['user']['language'])
        chatBot = chatBots[roomId]
        emit('message', make_message(chatBot.reply_with(json.text)))
        return

    # stage == 2
    # get doctor's language_code
    # Warning: Only handling the last joined doctor's language
    doctor_lan = db.user_op.get_user_full(doctors[-1])['language']

    # if speaks the same language, do not translate
    if doctor_lan == session['user']['language']:
        doctor_lan = None

    emit('message', make_message(json['message'], doctor_lan), to=roomId)
