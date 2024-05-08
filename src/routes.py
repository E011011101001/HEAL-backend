from flask import Blueprint, redirect, request, jsonify, make_response
import traceback

from . import app
from .route_decorators import required_body_items

from peewee import DoesNotExist, IntegrityError

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

@app.route('/users/<int:userId_patient>', methods=['GET'])
def get_users(userId_patient):
    try:
        userData = todo.get_patient_details(userId_patient)
        return userData, 200

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/users/<int:userId>', methods=['PUT'])
def update_users(userId):
    try:
        data = request.get_json()
        newData = todo.update_user(userId, data)
        return newData, 200

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})


@app.route('/users/<int:userId>', methods=['DELETE'])
def delete_users(userId):
    try:
        todo.delete_user(userId)
        return '', 204

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/users/login', methods=['POST'])
@required_body_items(['username', 'password'])
def login():
    pass

@app.route('/users/verify-token', methods=['GET'])
def verify_token():
    pass

# chat manager
@app.route('/chats/new', methods=['POST'])
def create_room():
    try:
        id = todo.create_room_id()
        return jsonify({"roomId": id}), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/chats/<int:roomId>', methods=['GET','DELETE'])
def operate_room(roomId):
    if request.method == 'GET':
        try:
            roomData = todo.get_room_details(roomId)
            return roomData, 200

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'DELETE':
        try:
            todo.delete_room(roomId)
            return '', 204

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

@app.route('/chats/<int:roomId>/participants/<int:userId>', methods=['POST', 'DELETE'])
def participant_room(roomId, userId):
    if request.method == 'POST':
        try:
            data = todo.participant_room(roomId, userId)
            return data, 201

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'DELETE':
        try:
            data = todo.exit_room(roomId, userId)
            return data, 200

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

@app.route('/users/<int:userId>/chats', method=['GET'])
def get_rooms(userId):
    try:
        data = todo.get_participating_rooms(userId)
        return data, 200

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

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
            'error': 'argumentError',
            'message': 'Argument does not exist'
        }, 406

    try:
        data = todo.get_chat_messages(roomId, pageNum, limNum)
        return data, 200

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/chats/<int:roomId>/messages/<int:mesId>', method=['GET'])
def get_message(roomId, mesId):
    try:
        data = todo.get_message(roomId, mesId)
        return data, 200

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

# medical term manager
@app.route('/medical-terms', method=['POST'])
@required_body_items(['name', 'description'])
def create_term():
    try:
        data = request.get_json()
        newData = todo.create_term(data)
        return newData, 201

    # need to confirm data['name']??
    except IntegrityError:
        return {
            'error': 'conflictError',
            'message': 'This medical term already exists.'
        }, 409

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/medical-terms', method=['GET'])
def get_terms():
    try:
        data = todo.get_terms()
        return data, 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/medical-terms/<int:medicalTermId>', method=['GET', 'PUT', 'DELETE'])
def operate_single_term(medicalTermId):

    if request.method == 'GET':
        try:
            data = todo.get_single_term(medicalTermId)
            return data, 200

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'PUT':
        try:
            data = todo.update_term(medicalTermId)
            return data, 200

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'DELETE':
        try:
            data = todo.delete_term(medicalTermId)
            return data, 200

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

# linking term manager
@app.route('/messages/<int:mesId>/medical-terms', method=['GET'])
def get_linked_term(mesId):
    try:
        data = todo.get_linking_term(mesId)
        return data, 200

    except DoesNotExist:
        return {
            'error': 'instanceNotFoundError',
            'message': 'The specified item does not exist.'
        }, 404

    except Exception as e:
        traceback.print_exc()
        return jsonify({'status': 'ERROR'})

@app.route('/messages/<int:mesId>/medical-terms/<int:medicalTermId>', method=['POST', 'DELETE'])
def operate_linked_term(mesId, medicalTermId):
    if request.method == 'POST':
        try:
            data = todo.create_linking_term(mesId, medicalTermId)
            return data, 201

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})

    if request.method == 'DELETE':
        try:
            todo.delete_linking_term(mesId, medicalTermId)
            return '', 204

        except DoesNotExist:
            return {
                'error': 'instanceNotFoundError',
                'message': 'The specified item does not exist.'
            }, 404

        except Exception as e:
            traceback.print_exc()
            return jsonify({'status': 'ERROR'})
