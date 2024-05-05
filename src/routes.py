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

