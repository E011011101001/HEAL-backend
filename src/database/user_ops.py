from peewee import DoesNotExist
from datetime import datetime, timedelta

from .data_models import BaseUser, Doctor, Patient, Session
from ..utils import salted_hash, gen_session_token
from ..glovars import PATIENT, DOCTOR

def email_exists(email: str) -> bool:
    try:
        BaseUser.get(BaseUser.Email == email)
        return True
    except DoesNotExist:
        return False


def create_user(data):
    userType = 0
    if data.get('type') == 'PATIENT':
        userType = PATIENT
    elif data.get('type') == 'DOCTOR':
        userType = DOCTOR
    else:
        raise RuntimeError('user type error')

    newUser = BaseUser.create(
        Email=data.get('email'),
        Language_code=data.get('language'),
        Name=data.get('name'),
        Password=salted_hash(data.get('password')),
        Type=userType
    )
    newUser.save()

    if userType == PATIENT:
        newPatient = Patient.create(
            BaseUser_id=newUser.id,
            Date_of_birth=data.get('dateOfBirth'),
            Height=data.get('height'),
            Weight=data.get('weight')
        )
        newPatient.save()
    elif userType == DOCTOR:
        newDoctor = Doctor.create(
            BaseUser_id=newUser.id,
            Specialisation=data.get('specialisation'),
            Hospital=data.get('hospital')
        )
        newDoctor.save()

    return newUser.id


def get_user_full(userId: int) -> dict:
    baseUser = BaseUser.get(BaseUser.id == userId)
    ret = {
        'user_id': baseUser.id,
        "email": baseUser.Email,
        "language": baseUser.Language_code,
        "name" : baseUser.Name
    }

    if baseUser.Type == PATIENT:
        patient = baseUser.patient[0]
        ret['type'] = 'PATIENT'
        ret['dateOfBirth'] = patient.Date_of_birth
        ret['height'] = patient.Height
        ret['weight'] = patient.Weight
    else:
        doctor = baseUser.doctor[0]
        ret['type'] = 'DOCTOR'
        ret['hospital'] = doctor.Hospital
        ret['specialisation'] = doctor.Specialisation

    return ret


def get_user_and_password(email: str) -> dict:
    user = BaseUser.get(BaseUser.Email == email)
    return {
        'id': user.id,
        'password': user.Password
    }


'''
    return
        session string
'''
def new_session_by_id(userId: int) -> str:
    token = gen_session_token()
    newSession = Session.create(
        User_id=userId,
        Token=token,
        Valid_until=datetime.now() + timedelta(days=2)
    )
    return token


def get_user_by_token(token) -> dict | None:

    try:
        session = Session.get(Session.Token == token)
    except DoesNotExist:
            return None

    return {
        'id': session.User_id,
        'expirationTime': session.Valid_until
    }

def update_user(userId: int, userUpdateInfo: dict):
    # get user with userid from database
    baseUser = BaseUser.get(BaseUser.id == userId)

    # update parts of user we need to
    if 'name' in userUpdateInfo:
        baseUser.Name = userUpdateInfo.get('name')

    if 'email' in userUpdateInfo:
        baseUser.Email = userUpdateInfo.get('email')

    if 'language' in userUpdateInfo:
        baseUser.Language = userUpdateInfo.get('language')

    # HANDLE PATIENT/DOCTOR - currently broken
    if baseUser.Type == PATIENT:
        patient = baseUser.patient[0]
        if 'date0fBirth' in userUpdateInfo:
            patient.Date0fBirth = userUpdateInfo.get('date0fBirth')
        if 'height' in userUpdateInfo:
            patient.Height = userUpdateInfo.get('height')
        if 'weight' in userUpdateInfo:
            patient.Weight = userUpdateInfo.get('weight')
        patient.save()
    else:
        doctor = baseUser.doctor[0]
        if 'hostpial' in userUpdateInfo:
            doctor.Hostpial = userUpdateInfo.get('hostpial')
        if 'specialisation' in userUpdateInfo:
            doctor.Specialisation = userUpdateInfo.get('specialisation')
        doctor.save()

    # save user back to database
    baseUser.save()

    return baseUser

# delete user information
def delete_user(userId: int):
    baseUser = BaseUser.get(BaseUser.id == userId)
    baseUser.delete_instance()
    return
