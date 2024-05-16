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

def delete_linking_term(messageId: int, termId: int):
    pass

def update_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescriptionInfo: dict) -> dict:
    prescription = PatientPrescription.get(PatientPrescription.UserCondition_id == prescriptionTermId, PatientPrescription.MedicalTerm_id == conditionTermId)

    if 'dosage' in prescriptionInfo:
        prescription.Dosage = prescriptionInfo.get('dosage')

    if 'Prescription_date' in prescriptionInfo:
        prescription.Perscription_date = prescriptionInfo.get('Prescription_date')

    prescription.save()
    return prescription

# This is wrong it should take UserCondition_id and MedicalTerm_id I think
def delete_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescriptionInfo: dict) -> dict:
    prescription = PatientPrescription.get(PatientPrescription.UserCondition_id == prescriptionTermId, PatientPrescription.MedicalTerm_id == conditionTermId)
    prescription.delete_instance()
    return
