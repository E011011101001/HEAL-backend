### user ###
from peewee import DoesNotExist
from datetime import datetime, timedelta

from .data_models import BaseUser, Doctor, Patient, Session, Room, MedicalTerm, PatientCondition, PatientPrescription, Message
from ..utils import salted_hash, gen_session_token
from ..glovars import PATIENT, DOCTOR
from .user_ops import get_user_full
from playhouse.shortcuts import model_to_dict


'''
update user details

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-37d7339d-15c4-41a7-91ce-4ee009dbe0b4
'''
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

# delete room corresponding to room id
def delete_room(roomId: int):
    room = Room.get(Room.id == roomId)
    room.delete_instance()
    return

def update_term(termId: int) -> dict:
    pass

def delete_term(termId: int):
    term = MedicalTerm.get(MedicalTerm.id == termId)
    term.delete_instance()
    return

def delete_linking_term(messageId: int, termId: int):
    pass

### patient medical history ###

def update_condition(userId: int, termId: int, conditionInfo: dict) -> dict:
    pass

def delete_condition(userId: int, termId: int, conditionInfo: dict) -> dict:
    condition = PatientCondition.get(PatientCondition.MedicalTerm_id == termId, PatientCondition.Patient_id == userId)
    condition.delete_instance()
    return

def update_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict) -> dict:
    pass

# This is wrong it should take UserCondition_id and MedicalTerm_id I think
def delete_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict) -> dict:
    condition = PatientPrescription.get(PatientPrescription.UserCondition_id == prescriptionTermId, PatientPrescription.MedicalTerm_id == conditionTermId)
    condition.delete_instance()
    return
