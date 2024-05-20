# src/routes.py
from flask import request, jsonify
from peewee import IntegrityError
from datetime import datetime

from . import app
from .route_decorators import required_body_items, required_params, login_required
from .utils import salted_hash
from . import database as db


# User Management
@app.route('/users/register', methods=['POST'])
@required_body_items(['type', 'email', 'password', 'name'])
def user_register():
    """
    Register a new user.

    Request JSON body example:
    {
        "type": "PATIENT",
        "email": "new_patient@gmail.com",
        "password": "securepassword",
        "name": "Jane Doe",
        "language": "en"
    }

    Response:
    {
        "userId": 1
    }
    201 Created
    """
    data = request.get_json()
    user_type = data.get('type')
    if user_type not in ['PATIENT', 'DOCTOR']:
        return {
            'error': 'TypeError',
            'message': '"type" must be either "PATIENT" or "DOCTOR".'
        }, 406

    if user_type == 'DOCTOR' and not data.get('specialisation'):
        return {
            'error': 'Missing items.',
            'missing': ['specialisation']
        }, 406

    if db.user.email_exists(data.get('email')):
        return {
            'error': 'conflictError',
            'message': 'An account with this email address already exists.'
        }, 409

    data.setdefault('language', 'en')
    return {
        'userId': db.user.create_user(data)
    }, 201


@app.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(_, __, user_id):
    """
    Get user details.

    URL Parameters:
    user_id: int - ID of the user

    Response:
    {
        "id": 1,
        "email": "test@gmail.com",
        "language_code": "en",
        "name": "John Doe",
        "user_type": 1,
        "date_of_birth": "1990-12-25"
    }
    200 OK
    """
    user_data = db.user.get_user_full(user_id)
    return user_data


@app.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(_, __, user_id):
    """
    Update user details.

    URL Parameters:
    user_id: int - ID of the user

    Request JSON body example:
    {
        "email": "updated_patient@gmail.com",
        "name": "John Updated",
        "dateOfBirth": "1990-12-26",
        "height": 180,
        "weight": 75
    }

    Response:
    {
        "id": 1,
        "email": "updated_patient@gmail.com",
        "language_code": "en",
        "name": "John Updated",
        "user_type": 1,
        "date_of_birth": "1990-12-26"
    }
    200 OK
    """
    data = request.get_json()

    if data.get('type') and data['type'] not in ['PATIENT', 'DOCTOR']:
        return {
            'error': 'TypeError',
            'message': "'type' must be either 'PATIENT' or 'DOCTOR'."
        }, 406

    if (data.get('email') and
            db.user.email_exists(data['email']) and
            db.user.get_user_full(user_id)['email'] != data['email']):
        return {
            'error': 'conflictError',
            'message': 'An account with this email address already exists.'
        }, 409

    if data.get('dateOfBirth'):
        try:
            datetime.strptime(data['dateOfBirth'], '%Y-%m-%d')
        except ValueError:
            return {
                'error': 'TypeError',
                'message': "'dateOfBirth' must be 'YYYY-MM-DD'."
            }, 406

    if data.get('height') is not None and data['height'] < 0:
        return {
            'error': 'TypeError',
            'message': "'height' must be a positive number"
        }, 406

    if data.get('weight') is not None and data['weight'] < 0:
        return {
            'error': 'TypeError',
            'message': "'weight' must be a positive number"
        }, 406

    db.user_op.update_user(user_id, data)
    user_data = db.user.get_user_full(user_id)
    return user_data, 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(_, __, user_id):
    """
    Delete a user.

    URL Parameters:
    user_id: int - ID of the user

    Response:
    204 No Content
    """
    db.user_op.delete_user(user_id)
    return '', 204


@app.route('/users/login', methods=['POST'])
@required_body_items(['email', 'password'])
def login():
    """
    Log in a user.

    Request JSON body example:
    {
        "email": "test@gmail.com",
        "password": "password"
    }

    Response:
    {
        "user": {
            "id": 1,
            "email": "test@gmail.com",
            "language_code": "en",
            "name": "John Doe",
            "user_type": 1,
            "date_of_birth": "1990-12-25"
        },
        "token": "example_token"
    }
    200 OK
    """
    data = request.get_json()
    failed = False
    try:
        user = db.user.get_user_and_password(data['email'])
        failed = user['password'] != salted_hash(data['password'])
    except Exception:
        failed = True

    if failed:
        return {
            "error": "forbiddenError",
            "message": "You do not have enough permissions to perform this action."
        }, 403
    else:
        token = db.user.new_session_by_id(user['id'])
        return {
            'user': db.user.get_user_full(user['id']),
            'token': token
        }


@app.route('/users/verify-token', methods=['GET'])
@login_required
def verify_token(user_id, __):
    """
    Verify user token.

    Response:
    {
        "id": 1,
        "email": "test@gmail.com",
        "language_code": "en",
        "name": "John Doe",
        "user_type": 1,
        "date_of_birth": "1990-12-25"
    }
    200 OK
    """
    return get_user(user_id)


# Chat Manager
@app.route('/chats/new', methods=['POST'])
@login_required
def create_room(user_id, _):
    """
    Create a new chat room.

    Request:
    {}

    Response:
    {
        "roomId": 1
    }
    201 Created
    """
    user_data = db.user.get_user_full(user_id)
    if user_data['type'] == 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only patients can create rooms."
        }

    room_id = db.room_op.create_room(user_id)
    return {'roomId': room_id}, 201


@app.route('/chats/<int:room_id>', methods=['GET', 'DELETE'])
@login_required
def operate_room(_, __, room_id):
    """
    Get or delete a chat room.

    URL Parameters:
    room_id: int - ID of the room

    GET Response:
    {
        "roomId": 1,
        "roomName": "",
        "creationTime": "2023-01-01T12:00:00",
        "participants": [
            {
                "id": 1,
                "email": "test@gmail.com",
                "language_code": "en",
                "name": "John Doe",
                "user_type": 1,
                "date_of_birth": "1990-12-25"
            },
            {
                "id": 2,
                "email": "doctor@gmail.com",
                "language_code": "jp",
                "name": "Dr. Smith",
                "user_type": 2,
                "date_of_birth": "1980-02-15"
            }
        ]
    }
    200 OK

    DELETE Response:
    204 No Content
    """
    if request.method == 'GET':
        room_data = db.room_op.get_room(room_id)
        return room_data

    db.room_op.delete_room(room_id)
    return '', 204


@app.route('/chats/<int:room_id>/participants/<int:participant_id>', methods=['POST', 'DELETE'])
@login_required
def participant_room(_, __, room_id, participant_id):
    """
    Add or remove a participant from a chat room.

    URL Parameters:
    room_id: int - ID of the room
    participant_id: int - ID of the participant

    POST Response:
    201 Created

    DELETE Response:
    204 No Content
    """
    user_data = db.user.get_user_full(participant_id)
    if user_data['type'] == 'PATIENT':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can enter and leave rooms."
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

    db.room_op.leave_room(participant_id, room_id)
    data = db.room_op.get_room(room_id)
    return data, 200


@app.route('/users/chats', methods=['GET'])
@login_required
def get_rooms(user_id, _):
    """
    Get all chat rooms for a user.

    Response:
    {
        "rooms": [
            {
                "roomId": 1,
                "roomName": "",
                "creationTime": "2023-01-01T12:00:00",
                "participants": [
                    {
                        "id": 1,
                        "email": "test@gmail.com",
                        "language_code": "en",
                        "name": "John Doe",
                        "user_type": 1,
                        "date_of_birth": "1990-12-25"
                    },
                    {
                        "id": 2,
                        "email": "doctor@gmail.com",
                        "language_code": "jp",
                        "name": "Dr. Smith",
                        "user_type": 2,
                        "date_of_birth": "1980-02-15"
                    }
                ]
            }
        ]
    }
    200 OK
    """
    data = db.room_op.get_rooms_all(user_id)
    return data, 200

@app.route('/users/chats/requests', methods=['GET'])
@login_required
def get_requested_rooms(user_id, _):
    """
    Get all chat rooms for a that a doctor has been requested to join.

    Response:
    {
        "rooms": [
            {
                "roomId": 1,
                "roomName": "",
                "creationTime": "2023-01-01T12:00:00",
                "participants": [
                    {
                        "id": 1,
                        "email": "test@gmail.com",
                        "language_code": "en",
                        "name": "John Doe",
                        "user_type": 1,
                        "date_of_birth": "1990-12-25"
                    },
                    {
                        "id": 2,
                        "email": "doctor@gmail.com",
                        "language_code": "jp",
                        "name": "Dr. Smith",
                        "user_type": 2,
                        "date_of_birth": "1980-02-15"
                    }
                ]
            }
        ]
    }
    200 OK
    """
    user_data = db.user.get_user_full(user_id)
    if user_data['type'] == 'PATIENT':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can get hospital room requests."
        }

    data = db.room_op.get_room_requests_all()
    return data, 200

# Message Management
@app.route('/chats/<int:room_id>/messages', methods=['GET'])
@required_params(['page', 'limit'])
@login_required
def get_chat_messages(_, language_code, room_id):
    """
    Get messages in a chat room.

    URL Parameters:
    room_id: int - ID of the room

    Request Parameters:
    page: int - Page number
    limit: int - Number of messages per page

    Response:
    {
        "messages": [
            {
                "id": 1,
                "user": {
                    "id": 1,
                    "email": "test@gmail.com",
                    "language_code": "en",
                    "name": "John Doe",
                    "user_type": 1,
                    "date_of_birth": "1990-12-25"
                },
                "room": 1,
                "text": "Hi, I've lost my sense of taste and I'm coughing a lot.",
                "send_time": "2023-01-01T12:00:00"
            },
            {
                "id": 2,
                "user": {
                    "id": 2,
                    "email": "doctor@gmail.com",
                    "language_code": "jp",
                    "name": "Dr. Smith",
                    "user_type": 2,
                    "date_of_birth": "1980-02-15"
                },
                "room": 1,
                "text": "新型コロナウイルス感染症に感染している場合は家にいてください",
                "send_time": "2023-01-01T12:05:00"
            }
        ]
    }
    200 OK
    """
    try:
        page_num = int(request.args.get('page'))
        limit_num = int(request.args.get('limit'))
        data = db.message_op.get_chat_messages(room_id, page_num, limit_num, language_code)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/chats/<int:room_id>/messages/<int:mes_id>', methods=['GET'])
@login_required
def get_message(_, language_code, room_id, mes_id):
    """
    Get a single message.

    URL Parameters:
    room_id: int - ID of the room
    mes_id: int - ID of the message

    Response:
    {
        "id": 1,
        "user": {
            "id": 1,
            "email": "test@gmail.com",
            "language_code": "en",
            "name": "John Doe",
            "user_type": 1,
            "date_of_birth": "1990-12-25"
        },
        "room": 1,
        "text": "Hi, I've lost my sense of taste and I'm coughing a lot.",
        "send_time": "2023-01-01T12:00:00"
    }
    200 OK
    """
    data = db.message_op.get_message(room_id, mes_id, language_code)
    return data, 200


# Medical Term Management
@app.route('/medical-terms', methods=['POST'])
@login_required
@required_body_items(['termType', 'termInfoList'])
def create_term(_, __):
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
    {
        "termId": 1
    }
    201 Created
    """
    data = request.get_json()
    term_type = data['termType']
    term_info_list = data['termInfoList']

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
@login_required
def get_terms(_, language_code):
    """
    Get all medical terms.

    Request Parameters:
    language: str - Language code for the term information (default: 'en')

    Response:
    {
        "terms": [
            {
                "id": 1,
                "term_type": "CONDITION",
                "translations": [
                    {
                        "language_code": "en",
                        "name": "COVID-19",
                        "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                        "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/"
                    },
                    {
                        "language_code": "jp",
                        "name": "コロナウイルス",
                        "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                        "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
                    }
                ]
            }
        ]
    }
    200 OK
    """
    data = db.message_op.get_terms_all(language_code)
    return data


@app.route('/medical-terms/<int:medical_term_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def operate_single_term(_, language_code, medical_term_id):
    """
    Operate on a single medical term.

    URL Parameters:
    medical_term_id: int - ID of the medical term

    GET Response:
    {
        "id": 1,
        "term_type": "CONDITION",
        "translations": [
            {
                "language_code": "en",
                "name": "COVID-19",
                "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/"
            },
            {
                "language_code": "jp",
                "name": "コロナウイルス",
                "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
            }
        ]
    }
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


# Linking Term Management
@app.route('/messages/<int:mes_id>/medical-terms', methods=['GET'])
@login_required
def get_linked_term(_, language_code, mes_id):
    """
    Get all medical terms linked to a message.

    URL Parameters:
    mes_id: int - ID of the message

    Response:
    {
        "terms": [
            {
                "id": 1,
                "term_type": "CONDITION",
                "translations": [
                    {
                        "language_code": "en",
                        "name": "COVID-19",
                        "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                        "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/"
                    },
                    {
                        "language_code": "jp",
                        "name": "コロナウイルス",
                        "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                        "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
                    }
                ]
            }
        ]
    }
    200 OK
    """
    data = db.message_op.get_message_terms(mes_id, language_code)
    return data


@app.route('/messages/<int:mes_id>/medical-terms/<int:medical_term_id>', methods=['POST', 'DELETE'])
@login_required
def operate_linked_term(_, __, mes_id, medical_term_id):
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


# Medical History Management
@app.route('/patients/<int:patient_id>/medical-history', methods=['GET'])
@login_required
def get_medical_history(_, __, patient_id):
    """
    Get the medical history of a patient.

    URL Parameters:
    patient_id: int - ID of the patient

    Response:
    {
        "userId": 1,
        "medicalConditions": [
            {
                "userConditionId": 1,
                "medicalTerm": {
                    "id": 1,
                    "term_type": "CONDITION",
                    "translations": [
                        {
                            "language_code": "en",
                            "name": "COVID-19",
                            "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                            "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/"
                        },
                        {
                            "language_code": "jp",
                            "name": "コロナウイルス",
                            "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                            "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
                        }
                    ]
                },
                "status": "current",
                "diagnosisDate": "2022-01-01",
                "prescriptions": [
                    {
                        "userPrescriptionId": 1,
                        "medicalTerm": {
                            "id": 2,
                            "term_type": "PRESCRIPTION",
                            "translations": [
                                {
                                    "language_code": "en",
                                    "name": "Paracetamol",
                                    "description": "Paracetamol is used to treat pain and fever.",
                                    "url": "https://www.nhs.uk/medicines/paracetamol/"
                                },
                                {
                                    "language_code": "jp",
                                    "name": "パラセタモール",
                                    "description": "パラセタモールは痛みと発熱を治療するために使用されます。",
                                    "url": "https://www.nhs.uk/medicines/paracetamol/"
                                }
                            ]
                        },
                        "dosage": "500mg",
                        "prescriptionDate": "2023-01-01T12:00:00",
                        "frequency": "twice a day"
                    }
                ]
            }
        ]
    }
    200 OK
    """
    data = db.condition_op.get_history(patient_id)
    return data


@app.route('/patients/<int:patient_id>/conditions/<int:medical_term_id>', methods=['POST'])
@login_required
def create_patient_condition(user_id, __, patient_id, medical_term_id):
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
    if user_data['type'] != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can add conditions."
        }

    patient_data = db.user.get_user_full(patient_id)
    if patient_data['type'] != 'PATIENT':
        return {
            "error": "forbiddenError",
            "message": "Conditions can only be added to patients."
        }

    if db.condition_op.check_condition(patient_id, medical_term_id):
        return {
            'error': 'conflictError',
            'message': 'Condition already exists for this patient.'
        }, 409

    updated_conditions = db.condition_op.add_condition(patient_id, medical_term_id, data)
    return updated_conditions, 201


@app.route('/patients/conditions/<int:condition_id>', methods=['PUT'])
@login_required
def update_patient_condition(user_id, __, condition_id):
    """
    Update a condition for a patient.

    URL Parameters:
    condition_id: int - ID of the condition

    Request JSON body example:
    {
        "status": "resolved",
        "diagnosis_date": "2022-01-01",
        "resolution_date": "2022-02-01"  # Optional
    }

    Response:
    {
        "userConditionId": 1,
        "medicalTerm": {
            "id": 1,
            "term_type": "CONDITION",
            "translations": [
                {
                    "language_code": "en",
                    "name": "COVID-19",
                    "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                    "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/"
                },
                {
                    "language_code": "jp",
                    "name": "コロナウイルス",
                    "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                    "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
                }
            ]
        },
        "status": "resolved",
        "diagnosisDate": "2022-01-01",
        "resolutionDate": "2022-02-01"
    }
    200 OK
    """
    data = request.get_json()

    user_data = db.user.get_user_full(user_id)
    if user_data['type'] != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can update conditions."
        }

    updated_conditions = db.condition_op.update_condition(condition_id, data)
    return updated_conditions, 200


@app.route('/patients/conditions/<int:condition_id>', methods=['DELETE'])
@login_required
def delete_patient_condition(user_id, __, condition_id):
    """
    Delete a condition for a patient.

    URL Parameters:
    condition_id: int - ID of the condition

    Response:
    204 No Content
    """
    user_data = db.user.get_user_full(user_id)
    if user_data['type'] != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can delete conditions."
        }

    db.condition_op.delete_condition(condition_id)
    return '', 204


@app.route('/patients/conditions/<int:condition_id>/prescriptions/<int:medical_term_id>', methods=['POST'])
@login_required
def create_patient_prescription(user_id, __, condition_id, medical_term_id):
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
    if user_data['type'] != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can add prescriptions."
        }

    if db.condition_op.check_prescription(condition_id, medical_term_id):
        return {
            'error': 'conflictError',
            'message': 'Prescription already exists for this condition.'
        }, 409

    updated_conditions = db.condition_op.add_prescription(user_id, condition_id, medical_term_id, data)
    return updated_conditions, 201


@app.route('/patients/prescriptions/<int:prescription_id>', methods=['PUT'])
@login_required
def update_patient_prescription(user_id, __, prescription_id):
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
    {
        "userPrescriptionId": 1,
        "medicalTerm": {
            "id": 2,
            "term_type": "PRESCRIPTION",
            "translations": [
                {
                    "language_code": "en",
                    "name": "Paracetamol",
                    "description": "Paracetamol is used to treat pain and fever.",
                    "url": "https://www.nhs.uk/medicines/paracetamol/"
                },
                {
                    "language_code": "jp",
                    "name": "パラセタモール",
                    "description": "パラセタモールは痛みと発熱を治療するために使用されます。",
                    "url": "https://www.nhs.uk/medicines/paracetamol/"
                }
            ]
        },
        "dosage": "1000mg",
        "prescriptionDate": "2023-01-01T12:00:00",
        "frequency": "once a day"
    }
    200 OK
    """
    data = request.get_json()

    user_data = db.user.get_user_full(user_id)
    if user_data['type'] != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can update prescriptions."
        }

    updated_prescription = db.condition_op.update_prescription(prescription_id, data)
    return updated_prescription, 200


@app.route('/patients/prescriptions/<int:prescription_id>', methods=['DELETE'])
@login_required
def delete_patient_prescription(user_id, __, prescription_id):
    """
    Delete a prescription for a patient's condition.

    URL Parameters:
    prescription_id: int - ID of the prescription

    Response:
    204 No Content
    """
    user_data = db.user.get_user_full(user_id)
    if user_data['type'] != 'DOCTOR':
        return {
            "error": "forbiddenError",
            "message": "Only doctors can delete prescriptions."
        }

    db.condition_op.delete_prescription(prescription_id)
    return '', 204






"""
Specialised Doctor Screen Endpoints


Get pending pateint requests


Get all unapproved medical terms
"""




# Get all doctor users
@app.route('/users/doctors', methods=['GET'])
@login_required
def get_all_doctors(_, __):
    """
    Get all doctor users.

    Response:
    {
        "doctors": [
            {
                "id": 1,
                "email": "doctor1@example.com",
                "name": "Dr. John Doe",
                "specialisation": "Cardiology",
                "language_code": "en"
            },
            {
                "id": 2,
                "email": "doctor2@example.com",
                "name": "Dr. Jane Smith",
                "specialisation": "Dermatology",
                "language_code": "jp"
            }
        ]
    }
    200 OK
    """
    doctors = db.user.get_all_doctors()
    return jsonify({"doctors": doctors}), 200


# Get all patient users
@app.route('/users/patients', methods=['GET'])
@login_required
def get_all_patients(_, __):
    """
    Get all patient users.

    Response:
    {
        "patients": [
            {
                "id": 1,
                "email": "patient1@example.com",
                "name": "John Doe",
                "date_of_birth": "1990-12-25",
                "height": 180,
                "weight": 75,
                "language_code": "en"
            },
            {
                "id": 2,
                "email": "patient2@example.com",
                "name": "Jane Smith",
                "date_of_birth": "1985-02-15",
                "height": 165,
                "weight": 60,
                "language_code": "jp"
            }
        ]
    }
    200 OK
    """
    patients = db.user.get_all_patients()
    return jsonify({"patients": patients}), 200
