# src/websocket.py
from datetime import datetime

from flask import request
from flask_socketio import emit, disconnect, join_room

from . import socketio
from . import database as db
from src import GPT

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
        return list(filter(lambda session: session['sid'] == sid, wsSessions))[0]
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
    sid: str = request.sid  # type: ignore

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
    rooms = db.room_op.get_rooms_all_fixed(session['userId'])['rooms']
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
          f"    User ID: {session['user']['userId']};"
          f"    User Name: {session['user']['name']}.")

    # leaving rooms is done by the framework
    wsSessions.remove(session)


def save_client_message(session: dict, text: str, time_iso_format: str) -> int:
    message_id = db.message_op.save_message_only(
        session['user']['userId'],
        session['roomId'],
        text,
        datetime.fromisoformat(time_iso_format)
    )

    return message_id


def analyze_terms(text: str, text_lan: str) -> list[(int, int)]:
    """
    1. Get terms by GPT.
    2. If terms exists in the database, send the data stored in the database.
    3. If terms does not exist, ask GPT for information and possible wiki links of the term. Send the data, and
        store them in the database.
    :return: list of (term_id, synonym_id)
    """

    term_pairs = []
    terms = GPT.extract_medical_term(text_lan, text)
    for term in terms:
        found_synonyms = []
        for synonym in term['synonyms']:
            found_synonyms += list(db.data_models.MedicalTermSynonym.select()
                                   .where(db.data_models.MedicalTermSynonym.synonym == synonym))

        if len(found_synonyms) == 0:
            # It's new. So search for explanation, and save
            term_explanation = GPT.explain_medical_term(text_lan, term['term'])
            term_id = db.data_models.MedicalTerm.create(term_type=term_explanation['type']).id
            db.data_models.MedicalTermInfo.create(
                medical_term=term_id,
                language_code=text_lan,
                name=term['term'],
                description=term_explanation['description'],
                url=term_explanation['url']
            )
        else:
            term_id = found_synonyms[0].medical_term

        stored_synonyms = (db.data_models.MedicalTermSynonym.select()
                           .where(db.data_models.MedicalTermSynonym.medical_term == term_id))
        new_synonyms = [synonym for synonym in term['synonyms'] if synonym not in stored_synonyms]
        for new_syn in new_synonyms:
            db.data_models.MedicalTermSynonym.create(
                medical_term=term_id,
                synonym=new_syn,
                language_code=text_lan
            )

        syn_id = db.data_models.MedicalTermSynonym.get(db.data_models.MedicalTermSynonym.synonym == term['term']).id
        term_pairs.append((term_id, syn_id))

    return term_pairs


def make_message(message_id: int, src_lan: str, target_lan: str) -> None:
    """
    After analyzing the terms, store the terms in the message cache
    """
    msg_text = db.data_models.Message.get(db.data_models.Message.id == message_id).text

    if src_lan != target_lan:
        translation = GPT.translate_to(target_lan, msg_text)
        db.data_models.MessageTranslationCache.create(
            message=message_id,
            language_code=target_lan,
            translated_text=translation
        )
        translated_pairs = analyze_terms(translation, target_lan)
        for term_pair in translated_pairs:
            db.data_models.MessageTermCache.create(
                message=message_id,
                medical_term=term_pair[0],
                translated_synonym=term_pair[1]
            )
    else:
        # same language
        term_pairs = analyze_terms(msg_text, src_lan)
        for term_pair in term_pairs:
            db.data_models.MessageTermCache.create(
                message=message_id,
                medical_term=term_pair[0],
                original_synonym=term_pair[1]
            )


def chat_with_bot(session: dict, json: dict) -> int:
    """
    :return: message_id of the message generated by the bot
    """

    global chatBots
    roomId = session['roomId']
    user_msg = json['text']
    lan = session['user']['language']

    if chatBots.get(roomId) is None:
        chatBots[roomId] = GPT.get_ai_doctor(lan)
    chatBot = chatBots[roomId]

    bot_msg = chatBot.chat(user_msg)

    message_id = db.message_op.save_message_only(0, roomId, bot_msg, datetime.now())
    make_message(message_id, lan, lan)
    emit('message', db.message_op.get_message(roomId, message_id, lan), to=roomId)
    return message_id


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
    roomId = session['roomId']

    if json.get('text') is None or json.get('timestamp') is None:
        emit('error', {
            'error': 'missing items',
            'message': '"message" and "timestamp" are required'
        })
        return

    message_id = save_client_message(session, json['text'], json['timestamp'].split('Z')[0])
    emit(
        'message',
        db.message_op.get_message(roomId, message_id, session['user']['language']),
        to=session['sid']
    )

    """
    translation target. If session user is the patient, target_lan should be the doctor's lan. If session user is the
    doctor, target_lan should be the patient's lan.'
    """
    target_lan: str

    if session['user']['type'] == 'PATIENT':
        doctors = db.room_op.get_room_doctor_ids(roomId)
        if len(doctors) == 0:
            # stage == 1
            doctor_msg_id = chat_with_bot(session, json)
            target_lan = session['user']['language']
        else:
            # stage == 2, the user, patient, is chatting to a doctor.
            # This is the only situation where the backend only passes the received message to the room

            # get doctor's language_code. Warning: Only handling the last joined doctor's language
            target_lan = db.user_op.get_user_full(doctors[-1])['language']

            make_message(message_id, session['user']['language'], target_lan)

            emit('message', db.message_op.get_message(roomId, message_id, target_lan), to=roomId, include_self=False)
            return
    else:
        # User is a doctor
        doctor_msg_id = message_id
        patient_id = db.data_models.Room.get(db.data_models.Room.id == roomId).patient
        target_lan = db.data_models.BaseUser.get(db.data_models.BaseUser.id == patient_id).language_code
        make_message(doctor_msg_id, session['user']['language'], target_lan)

    # Forward enhanced message on to receiving client
    data = db.message_op.get_message(roomId, doctor_msg_id, target_lan)
    emit('message', data, to=roomId, include_self=False)


@socketio.on('ping-pong')
def pong_with_ping():
    """
    Should receive `{
        'message: 'ping'
    }`
    However, no need to check it. Just pong.
    """
    emit('ping-pong', {
        'message': 'pong'
    })
