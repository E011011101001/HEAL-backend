# src/database/user_op.py
from peewee import DoesNotExist
from datetime import datetime, timedelta

from .data_models import BaseUser, Doctor, Patient, Session
from ..utils import salted_hash, gen_session_token
from ..glovars import PATIENT, DOCTOR


def email_exists(email: str) -> bool:
    """
    Check if an email already exists.

    Parameters:
    email (str): Email address

    Returns:
    bool: True if the email exists, False otherwise
    """
    try:
        BaseUser.get(BaseUser.email == email)
        return True
    except DoesNotExist:
        return False


def create_user(data):
    """
    Create a new user.

    Parameters:
    data (dict): User information

    Example:
    {
        "type": "PATIENT",
        "email": "test@gmail.com",
        "password": "password",
        "name": "John Doe",
        "dateOfBirth": "1990-12-25",
        "height": 190,
        "weight": 115
    }

    Returns:
    int: ID of the newly created user
    """
    user_type = 0
    if data.get('type') == 'PATIENT':
        user_type = PATIENT
    elif data.get('type') == 'DOCTOR':
        user_type = DOCTOR
    else:
        raise RuntimeError('user type error')

    new_user = BaseUser.create(
        email=data.get('email'),
        language_code=data.get('language'),
        name=data.get('name'),
        password=salted_hash(data.get('password')),
        user_type=user_type,
        date_of_birth=data.get('dateOfBirth'),
    )
    new_user.save()

    if user_type == PATIENT:
        new_patient = Patient.create(
            base_user=new_user.id,
            height=data.get('height'),
            weight=data.get('weight')
        )
        new_patient.save()
    elif user_type == DOCTOR:
        new_doctor = Doctor.create(
            base_user=new_user.id,
            specialisation=data.get('specialisation'),
            hospital=data.get('hospital')
        )
        new_doctor.save()

    return new_user.id


def get_user_full(user_id: int) -> dict:
    """
    Get full details of a user.

    Parameters:
    user_id (int): ID of the user

    Returns:
    dict: User details
    """
    base_user = BaseUser.get(BaseUser.id == user_id)
    ret = {
        'userId': base_user.id,
        "email": base_user.email,
        "language": base_user.language_code,
        "name": base_user.name,
        "dateOfBirth": base_user.date_of_birth
    }

    if base_user.user_type == PATIENT:
        patient = base_user.patient[0]
        ret['type'] = 'PATIENT'
        ret['height'] = patient.height
        ret['weight'] = patient.weight
    else:
        doctor = base_user.doctor[0]
        ret['type'] = 'DOCTOR'
        ret['hospital'] = doctor.hospital
        ret['specialisation'] = doctor.specialisation

    return ret


def get_user_and_password(email: str) -> dict:
    """
    Get user ID and password by email.

    Parameters:
    email (str): Email address

    Returns:
    dict: User ID, language code, and password
    """
    user = BaseUser.get(BaseUser.email == email)
    return {
        'id': user.id,
        'language_code': user.language_code,
        'password': user.password
    }


def new_session_by_id(user_id: int) -> str:
    """
    Create a new session token for a user.

    Parameters:
    user_id (int): ID of the user

    Returns:
    str: New session token
    """
    token = gen_session_token()
    Session.create(
        user=user_id,
        token=token,
        valid_until=datetime.now() + timedelta(days=2)
    )
    return token


def get_session_by_token(token) -> dict | None:
    """
    Get (user id, expiration time)
    """
    try:
        session = Session.get(Session.token == token)
    except DoesNotExist:
        return None

    return {
        'userId': session.user.id,
        'expirationTime': session.valid_until
    }


def update_user(user_id: int, user_update_info: dict):
    """
    Update user details.

    Parameters:
    user_id (int): ID of the user
    user_update_info (dict): Updated user information

    Example:
    {
        "name": "John Doe Updated",
        "email": "newemail@gmail.com",
        "language": "jp",
        "dateOfBirth": "1990-12-25",
        "height": 190,
        "weight": 115,
        "hospital": "New Hospital",
        "specialisation": "New Specialisation"
    }

    Returns:
    BaseUser: Updated user object
    """
    base_user = BaseUser.get(BaseUser.id == user_id)

    if 'name' in user_update_info:
        base_user.name = user_update_info.get('name')

    if 'email' in user_update_info:
        base_user.email = user_update_info.get('email')

    if 'language' in user_update_info:
        base_user.language_code = user_update_info.get('language')

    if base_user.user_type == PATIENT:
        patient = base_user.patient[0]
        if 'dateOfBirth' in user_update_info:
            patient.date_of_birth = user_update_info.get('dateOfBirth')
        if 'height' in user_update_info:
            patient.height = user_update_info.get('height')
        if 'weight' in user_update_info:
            patient.weight = user_update_info.get('weight')
        patient.save()
    else:
        doctor = base_user.doctor[0]
        if 'hospital' in user_update_info:
            doctor.hospital = user_update_info.get('hospital')
        if 'specialisation' in user_update_info:
            doctor.specialisation = user_update_info.get('specialisation')
        doctor.save()

    base_user.save()
    return base_user


def delete_user(user_id: int):
    """
    Delete a user.

    Parameters:
    user_id (int): ID of the user
    """
    base_user = BaseUser.get(BaseUser.id == user_id)
    base_user.delete_instance()

def get_all_doctors() -> list:
    """
    Get all doctor users.

    Returns:
    list: List of doctor users
    """
    query = BaseUser.select().join(Doctor).where(BaseUser.user_type == DOCTOR)
    doctors = [
        {
            "id": doctor.id,
            "email": doctor.email,
            "name": doctor.name,
            # "specialisation": doctor.doctor.specialisation,
            "language_code": doctor.language_code
        }
        for doctor in query
    ]
    return doctors

def get_all_patients() -> list:
    """
    Get all patient users.

    Returns:
    list: List of patient users
    """
    query = BaseUser.select().join(Patient).where(BaseUser.user_type == PATIENT)
    patients = [
        {
            "id": patient.id,
            "email": patient.email,
            "name": patient.name,
            "date_of_birth": patient.date_of_birth.strftime('%Y-%m-%d'),
            "height": patient.patient.height,
            "weight": patient.patient.weight,
            "language_code": patient.language_code
        }
        for patient in query
    ]
    return patients