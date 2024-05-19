# src/websocket.py
from datetime import datetime
from flask import request
from flask_socketio import emit, disconnect, join_room

from . import socketio
from . import database as db
from src.GPT import get_ai_doctor

wsSessions = []
chatBots = {}

def get_session() -> dict:
    global wsSessions
    sid = request.sid
    try:
        return next(session for session in wsSessions if session['sid'] == sid)
    except StopIteration:
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
            'message': '"message" and "timestamp" are required'
        })
        return

    message_id = save_client_message(user_id, room_id, json['text'], json['timestamp'].split('Z')[0])
    doctors = db.room_op.get_room_doctor_ids(room_id)
    
    if len(doctors) == 1:
        # Step 1: Chatbot response
        bot_message_id = chat_with_bot(session, json['text'])
        bot_message = db.message_op.get_message(room_id, bot_message_id, session['user']['language'])
        emit('message', bot_message, to=room_id)
    else:
        # Step 2 and Step 3: Real doctor(s) in the room
        for doctor_id in doctors:
            doctor_language = db.user.get_user_full(doctor_id)['language']
            enhanced_message = db.message_op.get_message(room_id, message_id, doctor_language)
            emit('message', enhanced_message, to=room_id)

        # Send the message back to the original sender
        original_message = db.message_op.get_message(room_id, message_id, session['user']['language'])
        emit('message', original_message, to=request.sid)

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
    wsSessions.append({
        'user': db.user.get_user_full(session['userId']),
        'roomId': room_id,
        'sid': sid
    })

@socketio.on('disconnect')
def on_disconnect():
    global wsSessions
    session = get_session()
    print(f"User disconnected:\n"
          f"    User ID: {session['user']['userId']};"
          f"    User Name: {session['user']['name']}.")
    wsSessions.remove(session)
