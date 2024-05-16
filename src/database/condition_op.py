# src/database/condition_op.py
from peewee import DoesNotExist
from datetime import datetime

from .data_models import PatientCondition, PatientPrescription
from .message_op import get_term

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

    patientConditions = PatientCondition.select().where(PatientCondition.Patient_id == userId)
    conditionList = []

    for patientCondition in patientConditions:
        conditionTermId = patientCondition.MedicalTerm_id
        conditionTermInfo = get_term(conditionTermId)

        patientPrescriptions  = PatientPrescription.select().where(PatientPrescription.UserCondition_id == conditionTermId)
        prescriptionList = []

        for patientPrescription in patientPrescriptions:
            prescriptionTermId = patientPrescription.MedicalTerm_id
            prescriptionInfo = get_term(prescriptionTermId)

            prescription = {
                "userPrescriptionId": patientPrescription.id,
                "medicalTerm": prescriptionInfo,
                "dosage": patientPrescription.Dosage,
                "prescriptionDate": patientPrescription.Prescription_date
            }

            prescriptionList.append(prescription)

        condition = {
            "userConditionId": conditionTermId,
            "medicalTerm": conditionTermInfo,
            "status": patientCondition.Status,
            "diagnosisDate": patientCondition.Diagnosis_date,
            "prescriptions": prescriptionList
        }

        conditionList.append(condition)

    ret = {
        "userId" : userId,
        "medicalConditions" : conditionList
    }

    return ret

def add_condition(userId: int, termId: int, conditionInfo: dict):
    newCondition = PatientCondition.create(
        MedicalTerm_id = termId,
        Patient_id = userId,
        Status = conditionInfo.get('status'),
        Diagnosis_date = conditionInfo.get('diagnosisDate'),
    )
    newCondition.save()

def update_condition(userId: int, termId: int, conditionInfo: dict):
    condition = PatientCondition.get(PatientCondition.MedicalTerm_id == termId, PatientCondition.Patient_id == userId)

    if 'status' in conditionInfo:
        condition.Status = conditionInfo.get('status')

    if 'diagnosis_date' in conditionInfo:
        condition.Diagnosis_date = conditionInfo.get('diagnosis_date')

    condition.save()
    return condition

def delete_condition(userId: int, termId: int, conditionInfo: dict):
    condition = PatientCondition.get(PatientCondition.MedicalTerm_id == termId, PatientCondition.Patient_id == userId)
    condition.delete_instance()
    return

def add_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict):
    p = PatientCondition.get((PatientCondition.Patient_id == userId) and (PatientCondition.MedicalTerm_id == conditionTermId))

    newPrescription = PatientPrescription.create(
        UserCondition_id = p.id,
        MedicalTerm_id = prescriptionTermId,
        Dosage = prescritptionInfo.get('dosage'),
        Prescription_date = prescritptionInfo.get('prescriptionDate')
    )

    newPrescription.save()

def update_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescriptionInfo: dict):
    prescription = PatientPrescription.get(PatientPrescription.UserCondition_id == prescriptionTermId, PatientPrescription.MedicalTerm_id == conditionTermId)

    if 'dosage' in prescriptionInfo:
        prescription.Dosage = prescriptionInfo.get('dosage')

    if 'Prescription_date' in prescriptionInfo:
        prescription.Perscription_date = prescriptionInfo.get('Prescription_date')

    prescription.save()
    return prescription

def delete_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescriptionInfo: dict):
    prescription = PatientPrescription.get(PatientPrescription.UserCondition_id == prescriptionTermId, PatientPrescription.MedicalTerm_id == conditionTermId)
    prescription.delete_instance()
    return

