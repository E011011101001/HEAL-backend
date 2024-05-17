from peewee import DoesNotExist
from datetime import datetime, timedelta

from .data_models import BaseUser, Doctor, Patient, Session
from ..utils import salted_hash, gen_session_token
from ..glovars import PATIENT, DOCTOR

def email_exists(email: str) -> bool:
    try:
        BaseUser.get(BaseUser.email == email)
        return True
    except DoesNotExist:
        return False

def create_user(data):
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
    user = BaseUser.get(BaseUser.email == email)
    return {
        'id': user.id,
        'language_code': user.language_code,
        'password': user.password
    }

def new_session_by_id(user_id: int) -> str:
    token = gen_session_token()
    new_session = Session.create(
        user=user_id,
        token=token,
        valid_until=datetime.now() + timedelta(days=2)
    )
    return token

def get_user_by_token(token) -> dict | None:
    try:
        session = Session.get(Session.token == token)
    except DoesNotExist:
        return None

    return {
        'id': session.user.id,
        'expirationTime': session.valid_until
    }

def update_user(user_id: int, user_update_info: dict):
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
    base_user = BaseUser.get(BaseUser.id == user_id)
    base_user.delete_instance()
    return
