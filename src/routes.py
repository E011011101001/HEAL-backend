from flask import Blueprint, redirect, request, make_response
import traceback
from peewee import IntegrityError

from . import app
from .route_decorators import required_body_items, required_params, login_required

from .utils import salted_hash

from . import database as db

from datetime import datetime

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

    return {
        'userId': db.user.create_user(data)
    }, 201


@app.route('/users/<int:userId>', methods=['GET'])
def get_users(userId):
    userData = db.user.get_user_full(userId)
    return userData


@app.route('/users/<int:userId>', methods=['PUT'])
def update_users(userId):
    data = request.get_json()

    # TODO: why traverse >> modified

    # confirm data structure
    if data.get('type') is not None:
        if data.get('type') != "PATIENT" or "DOCTOR":
            return {
                'error': 'TypeError',
                'message': '\'type\' must be either \'PATIENT\' or \'DOCTOR\'.'
            }, 406

    if data.get('email') is not None:
        if db.user.email_exists(data.get('email')):
            return {
                'error': 'conflictError',
                'message': 'An account with this email address already exists.'
            }, 409

    if data.get('dateOfBirth') is not None:
        try:
            datetime.strptime(data.get('dateOfBirth'), '%Y-%m-%d')
        except ValueError:
            return {
                'error': 'TypeError',
                'message': '\'dateOfBirth\' must be \'YYYY-MM-DD\'.'
            }, 406

    if data.get('height') is not None:
        if data.get('height') < 0:
            return {
                'error': 'TypeError',
                'message': '\'height\' must be positive number'
            }, 406

    if data.get('weight') is not None:
        if data.get('weight') < 0:
            return {
                'error': 'TypeError',
                'message': '\'weight\' must be positive number'
            }, 406

    # update user
    todo.update_user(userId, data)

    # TODO: logic wrong. Check the user type and use the corresponding getter
    # # get user details
    # newData = todo.get_user(userId)

    # return newData
    # TODO

    userData = db.user.get_user_full(userId)
    return userData, 200


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
@login_required
def verify_token(userId):
    return get_users(userId)

# chat manager
@app.route('/chats/new', methods=['POST'])
@login_required
def create_room(userId):
    userData = db.user.get_user_full(userId)
    if userData.get('type') == 'DOCTOR':
        # doctor try to create the room
        return {
            "error": "forbiddenError",
            "message": "Only patient can create the room."
        }

    id = db.room_op.create_room(userId)
    return {'roomId': id}, 201


@app.route('/chats/<int:roomId>', methods=['GET','DELETE'])
@login_required
def operate_room(_, roomId):
    if request.method == 'GET':
        roomData = db.room_op.get_room(roomId)
        return roomData

    # if request.method == 'DELETE':
    db.room_op.delete_room(roomId)
    return '', 204


@app.route('/chats/<int:roomId>/participants/<int:userId>', methods=['POST', 'DELETE'])
@login_required
def participant_room(_, roomId, userId):
    userData = db.user.get_user_full(userId)
    if userData.get('type') == 'PATIENT':
        # patient try to enter the room
        return {
            "error": "forbiddenError",
            "message": "Only doctor can enter the room."
        }

    if request.method == 'POST':
        db.room_op.participant_room(userId, roomId)
        data = db.room_op.get_room(roomId)
        return data, 201

    # if request.method == 'DELETE':
    todo.exit_room(roomId, userId)
    data = db.room_op.get_room(roomId)
    return data


@app.route('/users/<int:userId>/chats', methods=['GET'])
@login_required
def get_rooms(_, userId):
    userData = db.user.get_user_full(userId)
    if userData.get('type') == 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only patient can get the rooms."
        }

    data = db.room_op.get_rooms_all(userId)
    return data

# message manager
@app.route('/chats/<int:roomId>/messages', methods=['GET'])
@required_params(['page', 'limit'])
@login_required
def get_chat_messages(_, roomId):
    pageNum = request.args.get('page'); assert pageNum is not None

    limNum = request.args.get('limit'); assert limNum is not None

    data = db.message_op.get_chat_messages(roomId, int(pageNum), int(limNum))
    return data


@app.route('/chats/<int:roomId>/messages/<int:mesId>', methods=['GET'])
@login_required
def get_message(_, roomId, mesId):
    data = db.message_op.get_message(roomId, mesId)
    return data


# medical term manager
@app.route('/medical-terms', methods=['POST'])
@required_body_items(['name', 'description'])
def create_term():
    data = request.get_json()
    # check term name
    newData = db.message_op.create_term(data)
    return newData, 201


@app.route('/medical-terms', methods=['GET'])
def get_terms():
    data = db.message_op.get_terms_all()
    return data


@app.route('/medical-terms/<int:medicalTermId>', methods=['GET', 'PUT', 'DELETE'])
def operate_single_term(medicalTermId):
    #check medicalTermId

    if request.method == 'GET':
        data = db.message_op.get_term(medicalTermId)
        return data

    # required check Body
    if request.method == 'PUT':
        data = todo.update_term(medicalTermId, medicalTermInfo)
        return data

    # if request.method == 'DELETE':
    todo.delete_term(medicalTermId)
    return '', 204

# linking term manager
@app.route('/messages/<int:mesId>/medical-terms', methods=['GET'])
@login_required
def get_linked_term(_, mesId):
    data = db.message_op.get_message_terms(mesId)
    return data


@app.route('/messages/<int:mesId>/medical-terms/<int:medicalTermId>', methods=['POST', 'DELETE'])
@login_required
def operate_linked_term(mesId, medicalTermId):
    if request.method == 'POST':
        # check link

        data = db.message_op.create_link(mesId, medicalTermId)
        return data, 201

    # if request.method == 'DELETE':
    # check link
    todo.delete_linking_term(mesId, medicalTermId)
    return '', 204


# medical history
@app.route('/patients/<int:userId>/medical-history', methods=['GET'])
@login_required
def get_medical_history(_, userId):
    data = db.condition_op.get_history(userId)
    return data


@app.route('/patients/<int:userId>/patient-conditions/<int:termId>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def add_condition(_, userId, termId):
    data = request.get_json()

    # check user Id type is patient
    userData = db.user.get_user_full(userId)
    if userData.get('type') == 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only patient can add the conditions."
        }

    status = data.get('status')
    diagDate = data.get('diagnosisDate')
    if not status in ['current', 'past']:
        return {
            'error': 'TypeError',
            'message': '\'status\' must be either \'current\' or \'past\'.'
        }, 406

    try:
        datetime.strptime(diagDate, '%Y-%m-%d')
    except ValueError:
        return {
            'error': 'TypeError',
            'message': '\'diagnosisDate\' must be \'YYYY-MM-DD\'.'
        }, 406

    if request.method == 'POST':
        if(db.condition_op.check_condition(userId, termId)):
            return {
            'error': 'conflictError',
            'message': 'Medical terms already linked to this message.'
        }, 409

        db.condition_op.add_condition(userId, termId, data)
        newData = db.condition_op.get_history(userId)
        return newData, 201

        # TODO

        # except IntegrityError:
        #     return {
        #         'error': 'conflictError',
        #         'message': 'This condition medical term id already exists.'
        #     }, 409

    if request.method == 'PUT':
        if(db.condition_op.check_condition(userId, termId)):
            return {
            'error': 'conflictError',
            'message': 'Medical terms already linked to this message.'
        }, 409

        todo.update_condition(userId, termId, data)
        newData = db.condition_op.get_history(userId)
        return newData

    # if request.method == 'DELETE':
    todo.delete_condition(userId, termId, data)
    return '', 204


@app.route('/patients/<int:userId>/conditions/<int:conditionTermId>/prescriptions/<int:prescriptionTermId>', methods=['POST', 'PUT', 'DELETE'])
@login_required
def add_patient_prescription(userId, conditionTermId, prescriptionTermId):
    data = request.get_json()

    prescDate = data.get('prescriptionDate')
    try:
        datetime.strptime(prescDate, '%Y-%m-%d')
    except ValueError:
        return {
            'error': 'TypeError',
            'message': '\'prescriptionDate\' must be \'YYYY-MM-DD\'.'
        }, 406

    if request.method == 'POST':
        if(db.condition_op.check_prescription(userId, conditionTermId, prescriptionTermId)):
            return {
            'error': 'conflictError',
            'message': 'Medical terms already linked to this message.'
        }, 409

        db.condition_op.add_prescription(userId, conditionTermId, prescriptionTermId, data)
        newData = db.condition_op.get_history(userId)
        return newData, 201

        # TODO
        # except IntegrityError:
        #     return {
        #         'error': 'conflictError',
        #         'message': 'This medical term already exists.'
        #     }, 409
        #
        # already exist prescriptionTermId in conditionTermId, userId -> conflict error

    if request.method == 'PUT':
        if(db.condition_op.check_prescription(userId, conditionTermId, prescriptionTermId)):
            return {
            'error': 'conflictError',
            'message': 'Medical terms already linked to this message.'
        }, 409

        todo.update_prescription(userId, conditionTermId, prescriptionTermId, data)
        newData = db.condition_op.get_history(userId)
        return newData

    # if request.method == 'DELETE':
    todo.delete_prescription(userId, conditionTermId, prescriptionTermId, data)
    return '', 204
