from flask import Blueprint, redirect, request, make_response
import traceback
from peewee import IntegrityError

from . import app
from .route_decorators import required_body_items, required_params

from .utils import salted_hash

from . import database as db

# TODO: remove todo
from .database import todo


_todo = '', 500

@app.route('/users/register', methods=['POST'])
@required_body_items(['type', 'email', 'password', 'name'])
def user_register():
    PATIENT = 'PATIENT'
    DOCTOR = 'DOCTOR'
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

    db.user.create_user(data)

    return '', 201


@app.route('/users/<int:userId>', methods=['GET'])
def get_users(userId):
    userData = db.user.get_user_full(userId)
    return userData


@app.route('/users/<int:userId>', methods=['PUT'])
def update_users(userId):
    data = request.get_json()

    # TODO: why traverse

    # confirm data structure
    # for field in data:
    #     if field == 'type':
    #         if data['type'] != 'PATIENT' or 'DOCTOR':
    #             return {
    #                 'error': 'TypeError',
    #                 'message': 'Invalid type exist.'
    #             }, 404

    #     if field == 'height':
    #         if data['height'] >= 0:
    #             return {
    #                 'error': 'TypeError',
    #                 'message': 'Invalid type exist.'
    #             }, 404

    # update user
    todo.update_user(userId, data)

    # TODO: logic wrong. Check the user type and use the corresponding getter
    # # get user details
    # newData = todo.get_user(userId)

    # return newData
    # TODO
    return '', 500


@app.route('/users/<int:userId>', methods=['DELETE'])
def delete_users(userId):
    todo.delete_user(userId)
    return '', 204


@app.route('/users/login', methods=['POST'])
@required_body_items(['username', 'password'])
def login():
    data = request.get_json()
    failed = False
    try:
        user = db.user.get_user_and_password(data['username'])
        failed = user['password'] != salted_hash(data['password'])
    except Exception:
        failed = True
    finally:
        if failed:
            forbiddenError = {
                "error": "forbiddenError",
                "message": "You do not have enough permissions to perform this action."
            }
            return forbiddenError, 403
        else:
            token = db.user.new_session_by_id(user['id'])
            return {
                'user': get_users(user['id']),
                'token': token
            }



@app.route('/users/verify-token', methods=['GET'])
def verify_token():
    return _todo

# chat manager
@app.route('/chats/new', methods=['POST'])
def create_room():
    id = todo.create_room_id()
    return {'roomId': id}, 201


@app.route('/chats/<int:roomId>', methods=['GET','DELETE'])
def operate_room(roomId):
    if request.method == 'GET':
        roomData = todo.get_room_details(roomId)
        return roomData

    # if request.method == 'DELETE':
    todo.delete_room(roomId)
    return '', 204


@app.route('/chats/<int:roomId>/participants/<int:userId>', methods=['POST', 'DELETE'])
def participant_room(roomId, userId):
    if request.method == 'POST':
        data = todo.participant_room(roomId, userId)
        return data, 201

    # if request.method == 'DELETE':
    data = todo.exit_room(roomId, userId)
    return data


@app.route('/users/<int:userId>/chats', methods=['GET'])
def get_rooms(userId):
    data = todo.get_participanting_rooms(userId)
    return data


# message manager
@app.route('/chats/<int:roomId>/messages', methods=['GET'])
@required_params(['page', 'limit'])
def get_chat_messages(roomId):
    pageNum = request.args.get('page'); assert pageNum is not None

    limNum = request.args.get('limit'); assert limNum is not None

    data = todo.get_chat_messages(roomId, int(pageNum), int(limNum))
    return data


@app.route('/chats/<int:roomId>/messages/<int:mesId>', methods=['GET'])
def get_message(roomId, mesId):
    data = todo.get_message(roomId, mesId)
    return data


# medical term manager
@app.route('/medical-terms', methods=['POST'])
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


@app.route('/medical-terms', methods=['GET'])
def get_terms():
    data = todo.get_terms()
    return data


@app.route('/medical-terms/<int:medicalTermId>', methods=['GET', 'PUT', 'DELETE'])
def operate_single_term(medicalTermId):
    if request.method == 'GET':
        data = todo.get_single_term(medicalTermId)
        return data

    if request.method == 'PUT':
        data = todo.update_term(medicalTermId)
        return data

    # if request.method == 'DELETE':
    todo.delete_term(medicalTermId)
    return '', 204

# linking term manager
@app.route('/messages/<int:mesId>/medical-terms', methods=['GET'])
def get_linked_term(mesId):
    data = todo.get_linking_term(mesId)
    return data


@app.route('/messages/<int:mesId>/medical-terms/<int:medicalTermId>', methods=['POST', 'DELETE'])
def operate_linked_term(mesId, medicalTermId):
    if request.method == 'POST':
        data = todo.create_linking_term(mesId, medicalTermId)
        return data, 201

    # if request.method == 'DELETE':
    todo.delete_linking_term(mesId, medicalTermId)
    return '', 204


# medical history
@app.route('/patients/<int:userId>/medical-history', methods=['GET'])
def get_medical_history(userId):
    data = todo.get_history(userId)
    return data


@app.route('/patients/<int:userId>/patient-conditions/<int:termId>', methods=['POST', 'PUT', 'DELETE'])
def add_condition(userId, termId):
    data = request.get_json()
    if request.method == 'POST':
        newData = todo.add_condition(userId, termId, data)
        return newData, 201

        # TODO

        # except IntegrityError:
        #     return {
        #         'error': 'conflictError',
        #         'message': 'This medical term already exists.'
        #     }, 409

    if request.method == 'PUT':
        newData = todo.update_condition(userId, termId, data)
        return newData

    # if request.method == 'DELETE':
    todo.delete_condition(userId, termId, data)
    return '', 204


@app.route('/patients/<int:userId>/conditions/<int:conditionTermId>/prescriptions/<int:prescriptionTermId>', methods=['POST', 'PUT', 'DELETE'])
def add_patient_prescription(userId, conditionTermId, prescriptionTermId):
    data = request.get_json()
    if request.method == 'POST':
        newData = todo.add_prescription(userId, conditionTermId, prescriptionTermId, data)
        return newData, 201

        # TODO
        # except IntegrityError:
        #     return {
        #         'error': 'conflictError',
        #         'message': 'This medical term already exists.'
        #     }, 409

    if request.method == 'PUT':
        newData = todo.update_prescription(userId, conditionTermId, prescriptionTermId, data)
        return newData

    # if request.method == 'DELETE':
    todo.delete_prescription(userId, conditionTermId, prescriptionTermId, data)
    return '', 204
