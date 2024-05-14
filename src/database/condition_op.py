from peewee import DoesNotExist
from datetime import datetime

from .data_models import PatientCondition, PatientPrescription

def check_condition(userId, termId):
    try:
        PatientCondition.get((PatientCondition.Patient_id == userId) and (PatientCondition.MedicalTerm_id == termId))
        return True
    except DoesNotExist:
        return False

def check_prescription(userId, conditionTermId, prescriptionTermId):
    try:
        p = PatientCondition.get((PatientCondition.Patient_id == userId) and (PatientCondition.MedicalTerm_id == conditionTermId))
        PatientPrescription.get((PatientPrescription.UserCondition_id == p.id) and (PatientPrescription.MedicalTerm_id == prescriptionTermId))
        return True
    except DoesNotExist:
        return False

### patient medical history ###
def get_history(userId: int) -> dict:
    pass

def add_condition(userId: int, termId: int, conditionInfo: dict):
    newCondition = PatientCondition.create(
        MedicalTerm_id = termId,
        Patient_id = userId,
        Status = conditionInfo.get('status'),
        Diagnosis_date = conditionInfo.get('diagnosisDate'),
        Resolution_date = null
    )
    newCondition.save()

def update_condition(userId: int, termId: int, conditionInfo: dict):
    pass

def delete_condition(userId: int, termId: int, conditionInfo: dict):
    pass

def add_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict):
    pass

def update_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict):
    pass

def delete_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict):
    pass

