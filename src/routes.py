# src/routes.py
from flask import Blueprint, redirect, request, make_response, jsonify
import traceback
from peewee import IntegrityError

from . import app
from .route_decorators import required_body_items, required_params, login_required

from .utils import salted_hash

from . import database as db

from datetime import datetime

# TODO: remove todo
from .database import todo
from .database.data_models import BaseUser


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


@app.route('/users/<int:user_id>', methods=['GET'])
def get_users(user_id):
    userData = db.user.get_user_full(user_id)
    return userData


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_users(user_id):
    data = request.get_json()

    # TODO: why traverse >> modified

    # confirm data structure
    if data.get('type') is not None:
        if data.get('type') != "PATIENT" and data.get('type') != "DOCTOR":
            return {
                'error': 'TypeError',
                'message': '\'type\' must be either \'PATIENT\' or \'DOCTOR\'.'
            }, 406

    if data.get('email') is not None:
        if db.user.email_exists(data.get('email')) and db.user.get_user_full(user_id).get('email') != data.get('email'):
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
    db.user_op.update_user(user_id, data)

    # TODO: logic wrong. Check the user type and use the corresponding getter
    # # get user details
    # newData = todo.get_user(user_id)

    # return newData
    # TODO

    userData = db.user.get_user_full(user_id)
    return userData, 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_users(user_id):
    db.user_op.delete_user(user_id)
    return '', 204


@app.route('/users/login', methods=['POST'])
@required_body_items(['email', 'password'])
def login():
    data = request.get_json()
    failed = False
    try:
        user = db.user.get_user_and_password(data['email'])
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
def verify_token(user_id, language_code):
    return get_users(user_id)

# chat manager
@app.route('/chats/new', methods=['POST'])
@login_required
def create_room(user_id, language_code):
    userData = db.user.get_user_full(user_id)
    if userData.get('type') == 'DOCTOR':
        # doctor try to create the room
        return {
            "error": "forbiddenError",
            "message": "Only patient can create the room."
        }

    id = db.room_op.create_room(user_id)
    return {'roomId': id}, 201


@app.route('/chats/<int:roomId>', methods=['GET','DELETE'])
@login_required
def operate_room(user_id, language_code, roomId):
    if request.method == 'GET':
        roomData = db.room_op.get_room(roomId)
        return roomData

    # if request.method == 'DELETE':
    db.room_op.delete_room(roomId)
    return '', 204

@app.route('/chats/<int:room_id>/participants/<int:user_id>', methods=['POST', 'DELETE'])
@login_required
def participant_room(user_id, language_code, room_id, participant_id):
    user_data = db.user.get_user_full(participant_id)
    if user_data.get('type') == 'PATIENT':
        # patient try to enter or leave the room
        return {
            "error": "forbiddenError",
            "message": "Only doctor can enter and leave the room."
        }

    if request.method == 'POST':
        added = db.room_op.participant_room(participant_id, room_id)
        if not added:
            return {
                "error": "conflictError",
                "message": "The doctor is already in the room."
            }, 409

        data = db.room_op.get_room(room_id)
        return data, 201

    if request.method == 'DELETE':
        db.room_op.leave_room(participant_id, room_id)
        data = db.room_op.get_room(room_id)
        return data, 200

@app.route('/users/<int:user_id>/chats', methods=['GET'])
@login_required
def get_rooms(user_id, language_code):
    userData = db.user.get_user_full(user_id)
    if userData.get('type') == 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only patient can get the rooms."
        }

    data = db.room_op.get_rooms_all(user_id)
    return data, 200

# message manager
@app.route('/chats/<int:roomId>/messages', methods=['GET'])
@required_params(['page', 'limit'])
@login_required
def get_chat_messages(user_id, language_code, roomId):
    try:
        pageNum = request.args.get('page')
        limNum = request.args.get('limit')
        if pageNum is None or limNum is None:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        pageNum = int(pageNum)
        limNum = int(limNum)

        data = db.message_op.get_chat_messages(roomId, pageNum, limNum, language_code)
        print(data)
        return jsonify(data)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/chats/<int:roomId>/messages/<int:mesId>', methods=['GET'])
@login_required
def get_message(user_id, language_code, roomId, mesId):
    data = db.message_op.get_message(roomId, mesId, language_code)
    return data, 200


# medical term manager
@app.route('/medical-terms', methods=['POST'])
@required_body_items(['termType', 'termInfoList'])
def create_term():
    """
    Create a new medical term.

    Request JSON body example:
    {
        "termType": "CONDITION",
        "termInfoList": [
            {
                "language_code": "en",
                "name": "COVID-19",
                "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/",
                "synonyms": [
                    {"synonym": "COVID"},
                    {"synonym": "COVID-19"},
                    {"synonym": "Corona"},
                    {"synonym": "COVID 19"},
                    {"synonym": "Scary COVID"}
                ]
            },
            {
                "language_code": "jp",
                "name": "コロナウイルス",
                "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/",
                "synonyms": [
                    {"synonym": "コロナ"},
                    {"synonym": "新型コロナウイルス"}
                ]
            }
        ]
    }

    Response:
    201 Created
    """
    data = request.get_json()
    term_type = data.get('termType')
    term_info_list = data.get('termInfoList')

    # Check for required fields in term_info_list
    for term_info in term_info_list:
        if not term_info.get('name') or not term_info.get('description'):
            return {
                'error': 'Missing items.',
                'message': 'Each term_info must include "name" and "description".'
            }, 406

    try:
        new_term_id = db.message_op.create_term(term_type, term_info_list)
        return {'termId': new_term_id}, 201
    except Exception as e:
        return {
            'error': 'ServerError',
            'message': str(e)
        }, 500


@app.route('/medical-terms', methods=['GET'])
def get_terms():
    """
    Get all medical terms.

    Request Parameters:
    language: str - Language code for the term information (default: 'en')

    Response:
    200 OK
    """
    language_code = request.args.get('language', 'en')
    data = db.message_op.get_terms_all(language_code)
    return data

@app.route('/medical-terms/<int:medical_term_id>', methods=['GET', 'PUT', 'DELETE'])
def operate_single_term(medical_term_id):
    """
    Operate on a single medical term.

    URL Parameters:
    medical_term_id: int - ID of the medical term

    GET Response:
    200 OK

    PUT Request JSON body example:
    {
        "name": "COVID-19 Updated",
        "description": "Updated description.",
        "url": "https://updated-url.com",
        "synonyms": [
            {"synonym": "Updated COVID"},
            {"synonym": "Updated Corona"}
        ]
    }

    DELETE Response:
    204 No Content
    """
    # Get the user's language code from the request headers or other authentication mechanism
    language_code = request.headers.get('Language-Code', 'en')

    if request.method == 'GET':
        data = db.message_op.get_term(medical_term_id, language_code)
        return data

    if request.method == 'PUT':
        medical_term_info = request.get_json()
        data = db.message_op.update_term(medical_term_id, medical_term_info, language_code)
        return data

    if request.method == 'DELETE':
        db.message_op.delete_term(medical_term_id)
        return '', 204

# linking term manager
@app.route('/messages/<int:mesId>/medical-terms', methods=['GET'])
@login_required
def get_linked_term(user_id, language_code, mesId):
    """
    Get all medical terms linked to a message.

    URL Parameters:
    mesId: int - ID of the message

    Response:
    200 OK
    """
    data = db.message_op.get_message_terms(mesId, language_code)
    return data

@app.route('/messages/<int:mes_id>/medical-terms/<int:medical_term_id>', methods=['POST', 'DELETE'])
@login_required
def operate_linked_term(user_id, language_code, mes_id, medical_term_id):
    """
    Operate on medical terms linked to a message.

    URL Parameters:
    mes_id: int - ID of the message
    medical_term_id: int - ID of the medical term

    POST Response:
    201 Created

    DELETE Response:
    204 No Content
    """
    if request.method == 'POST':
        db.message_op.create_link(mes_id, medical_term_id)
        return '', 201

    if request.method == 'DELETE':
        db.message_op.delete_linking_term(mes_id, medical_term_id)
        return '', 204





# medical history
@app.route('/patients/<int:patient_id>/medical-history', methods=['GET'])
@login_required
def get_medical_history(user_id, language_code, patient_id):
    """
    Get the medical history of a patient.

    URL Parameters:
    patient_id: int - ID of the patient

    Response:
    200 OK
    """
    data = db.condition_op.get_history(patient_id)
    return data


@app.route('/patients/<int:patient_id>/conditions/<int:medical_term_id>', methods=['POST'])
@login_required
def create_patient_condition(user_id, language_code, patient_id, medical_term_id):
    """
    Create a new condition for a patient.

    URL Parameters:
    patient_id: int - ID of the patient
    medical_term_id: int - ID of the medical term

    Request JSON body example:
    {
        "status": "current",
        "diagnosis_date": "2022-01-01",
        "resolution_date": "2022-02-01"  # Optional
    }

    Response:
    201 Created
    """
    data = request.get_json()

    user_data = db.user.get_user_full(user_id)
    if user_data.get('type') != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can add conditions."
        }

    patient_data = db.user.get_user_full(patient_id)
    if patient_data.get('type') != 'PATIENT':
        return {
            "error": "forbiddenError",
            "message": "Conditions can only be added to patients."
        }

    if db.condition_op.check_condition(patient_id, medical_term_id):
        return {
            'error': 'conflictError',
            'message': 'Condition already exists for this patient.'
        }, 409

    db.condition_op.add_condition(patient_id, medical_term_id, data)
    return '', 201


@app.route('/patients/conditions/<int:condition_id>/<int:medical_term_id>', methods=['PUT'])
@login_required
def update_patient_condition(user_id, language_code, condition_id, medical_term_id):
    """
    Update a condition for a patient.

    URL Parameters:
    condition_id: int - ID of the condition
    medical_term_id: int - ID of the medical term

    Request JSON body example:
    {
        "status": "resolved",
        "diagnosis_date": "2022-01-01",
        "resolution_date": "2022-02-01"  # Optional
    }

    Response:
    200 OK
    """
    data = request.get_json()

    user_data = db.user.get_user_full(user_id)
    if user_data.get('type') != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can update conditions."
        }

    updated_condition = db.condition_op.update_condition(condition_id, medical_term_id, data, language_code)
    return updated_condition, 200


@app.route('/patients/conditions/<int:condition_id>', methods=['DELETE'])
@login_required
def delete_patient_condition(user_id, language_code, condition_id):
    """
    Delete a condition for a patient.

    URL Parameters:
    condition_id: int - ID of the condition

    Response:
    204 No Content
    """
    user_data = db.user.get_user_full(user_id)
    if user_data.get('type') != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can delete conditions."
        }

    db.condition_op.delete_condition(condition_id)
    return '', 204


@app.route('/patients/conditions/<int:condition_id>/prescriptions/<int:medical_term_id>', methods=['POST'])
@login_required
def create_patient_prescription(user_id, language_code, condition_id, medical_term_id):
    """
    Create a new prescription for a patient's condition.

    URL Parameters:
    condition_id: int - ID of the condition
    medical_term_id: int - ID of the medical term

    Request JSON body example:
    {
        "dosage": "500mg",
        "prescription_date": "2023-01-01T12:00:00",
        "frequency": "twice a day"
    }

    Response:
    201 Created
    """
    data = request.get_json()

    user_data = db.user.get_user_full(user_id)
    if user_data.get('type') != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can add prescriptions."
        }

    if db.condition_op.check_prescription(condition_id, medical_term_id):
        return {
            'error': 'conflictError',
            'message': 'Prescription already exists for this condition.'
        }, 409

    db.condition_op.add_prescription(user_id, condition_id, medical_term_id, data)
    return '', 201


@app.route('/patients/prescriptions/<int:prescription_id>', methods=['PUT'])
@login_required
def update_patient_prescription(user_id, language_code, prescription_id):
    """
    Update a prescription for a patient's condition.

    URL Parameters:
    prescription_id: int - ID of the prescription

    Request JSON body example:
    {
        "dosage": "1000mg",
        "prescription_date": "2023-01-01T12:00:00",
        "frequency": "once a day"
    }

    Response:
    200 OK
    """
    data = request.get_json()

    user_data = db.user.get_user_full(user_id)
    if user_data.get('type') != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can update prescriptions."
        }

    updated_prescription = db.condition_op.update_prescription(prescription_id, data)
    return updated_prescription, 200


@app.route('/patients/prescriptions/<int:prescription_id>', methods=['DELETE'])
@login_required
def delete_patient_prescription(user_id, language_code, prescription_id):
    """
    Delete a prescription for a patient's condition.

    URL Parameters:
    prescription_id: int - ID of the prescription

    Response:
    204 No Content
    """
    user_data = db.user.get_user_full(user_id)
    if user_data.get('type') != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can delete prescriptions."
        }

    db.condition_op.delete_prescription(prescription_id)
    return '', 204
