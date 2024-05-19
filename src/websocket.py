from datetime import datetime
from flask import request
from flask_socketio import emit, disconnect, join_room

from . import socketio
from . import database as db
from src.GPT.chatbot import get_ai_doctor

wsSessions = {}
chatBots = {}

def get_session() -> dict:
    sid = request.sid
    try:
        return wsSessions[sid]
    except KeyError:
        emit('error', {
            'error': 'InternalServerError',
            'message': 'User is authenticated. However, no registered sid is found.'
        })
        disconnect()
        raise

def save_client_message(user_id: int, room_id: int, text: str, timestamp: str) -> int:
    message_id = db.message_op.save_message_only(
        user_id,
        room_id,
        text,
        datetime.fromisoformat(timestamp)
    )
    return message_id

def chat_with_bot(session: dict, user_msg: str) -> int:
    global chatBots
    room_id = session['roomId']
    
    if room_id not in chatBots:
        chatBots[room_id] = get_ai_doctor(session['user']['language'])
    chatBot = chatBots[room_id]

    bot_msg = chatBot.chat(user_msg)
    message_id = db.message_op.save_message_only(0, room_id, bot_msg, datetime.now())
    
    return message_id

@socketio.on('message')
def handle_message(json: dict):
    session = get_session()
    room_id = session['roomId']
    user_id = session['user']['userId']

    if 'text' not in json or 'timestamp' not in json:
        emit('error', {
            'error': 'missing items',
            'message': '"text" and "timestamp" are required'
        })
        return

    # Save client message
    message_id = save_client_message(user_id, room_id, json['text'], json['timestamp'].split('Z')[0])
    
    # Get all users in the room
    room_users = db.room_op.get_room_doctor_ids(room_id)

    # Add the current user ID to the list if it's not already included
    if user_id not in room_users:
        room_users.append(user_id)

    # Send the message to all users in the room
    for user in room_users:
        user_language = db.user.get_user_full(user)['language']
        enhanced_message = db.message_op.get_message(room_id, message_id, user_language)
        if user in wsSessions:
            emit('message', enhanced_message, to=wsSessions[user]['sid'])

    # Check if there's only one doctor (the chatbot) in the room
    doctors = db.room_op.get_room_doctor_ids(room_id)
    if len(doctors) == 1:
        bot_message_id = chat_with_bot(session, json['text'])
        bot_message = db.message_op.get_message(room_id, bot_message_id, session['user']['language'])
        emit('message', bot_message, to=wsSessions[session['user']['userId']]['sid'])


@socketio.on('connect')
def connect(auth: dict):
    token = auth.get('token')
    room_id = auth.get('roomId')
    sid = request.sid

    unauthError = {'error': 'unauthorizationError'}

    session = db.user.get_session_by_token(token)
    if session and session['expirationTime'] < datetime.now():
        session = None

    if session is None:
        unauthError['message'] = 'User invalid'
        emit('error', unauthError)
        disconnect()
        return

    rooms = db.room_op.get_rooms_all(session['userId'])['rooms']
    room_ids = [room['roomId'] for room in rooms]

    if room_id not in room_ids:
        unauthError['message'] = 'Room invalid'
        emit('error', unauthError)
        disconnect()
        return

    join_room(room_id)
    wsSessions[sid] = {
        'user': db.user.get_user_full(session['userId']),
        'roomId': room_id,
        'sid': sid
    }

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    session = wsSessions.pop(sid, None)
    if session:
        print(f"User disconnected:\n"
              f"    User ID: {session['user']['userId']};"
              f"    User Name: {session['user']['name']}.")
