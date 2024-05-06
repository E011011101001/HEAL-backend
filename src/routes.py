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

@app.route('/chats/new', methods=['POST'])
def create_room():
    try:
        todo.create_room_id()
        return '', 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})
    
@app.route('/chats/<roomId>', methods=['GET'])
def get_retails(roomId):
    try:
        roomData = todo.get_room_details(roomId)
        return roomData, 201
    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})