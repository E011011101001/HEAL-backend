from peewee import DoesNotExist

from .data_models import BaseUser, Doctor, Patient
from ..utils import salted_hash
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
