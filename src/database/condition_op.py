from peewee import DoesNotExist

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
