from flask import Blueprint, redirect, request, jsonify, make_response
import traceback

from . import app
from .route_decorators import required_body_items

from . import database as db

# TODO: remove todo
from .database import todo

@app.route('/users/register', methods=['POST'])
@required_body_items(['type', 'email', 'password'])
def user_register():
    PATIENT = "PATIENT"
    DOCTOR = "DOCTOR"
    try:
        data = request.get_json()
        userType = data.get('type')
        if not userType in [PATIENT, DOCTOR]:
            return {
                'error': 'TypeError',
                'message': f'"type" must be either "{PATIENT}" or "{DOCTOR}".'
            }, 406

        if userType is DOCTOR:
            if not data.get('specialisation'):
                return {
                    'error': 'Missing items.',
                    'missing': ['specialisation']
                }, 406

        if db.user.email_exists(data.get('email')):
            return {
                'error': 'conflictError',
                'message': 'An account with this email address already exists.'
            }, 409

        # language default to 'en'
        if not data.get('language'):
            data['language'] = 'en'

        todo.create_user(data)
        return '', 201

    except Exception:
        traceback.print_exc()
        return {'status': 'ERROR'}

@app.route('/users/<userId_patient>', methods=['GET'])
def get_users(userId_patient):
    try:
        userData = todo.get_patient_details(userId_patient)
        return userData, 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

# chat manager
@app.route('/chats/new', methods=['POST'])
def create_room():
    try:
        id = todo.create_room_id()
        return jsonify({"roomId": id}), 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

# need to separate
@app.route('/chats/<int:roomId>', methods=['GET','DEL'])
def operate_room(roomId):
    if not todo.room_exists(roomId):
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

    if request.method == 'GET':
        try:
            roomData = todo.get_room_details(roomId)
            return roomData, 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'DEL':
        try:
            todo.delete_room(roomId)
            return '', 204
        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

@app.route('/chats/<int:roomId>/participants/<int:userId>', methods=['POST', 'DEL'])
def participant_room(roomId, userId):
    if request.method == 'POST':
        try:
            data = todo.participant_room(roomId, userId)
            return data, 201
        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'DEL':
        try:
            data = todo.exit_room(roomId, userId)
            return data, 200
        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

@app.route('/users/<int:userId>/chats', method=['GET'])
def get_rooms(userId):
    try:
        data = todo.get_participating_rooms(userId)
        return data, 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

# message manager
@app.route('/chats/<int:roomId>/messages', method=['GET'])
def get_chat_messages(roomId):

    try:
        pageNum = request.args["page"]
        limNum = request.args["limit"]
    except Exception as e:
        traceback.print_exc()
        return {
            'error': 'Error',
            'message': 'Argument does not exist'
        }, 406

    try:
        data = todo.get_chat_messages(roomId, pageNum, limNum)
        return data, 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/chats/<int:roomId>/messages/<int:mesId>', method=['GET'])
def get_message(roomId, mesId):
    try:
        data = todo.get_message(roomId, mesId)
        return data, 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

