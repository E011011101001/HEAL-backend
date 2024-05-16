from peewee import DoesNotExist
from datetime import datetime

from .data_models import PatientCondition, PatientPrescription
from .message_op import get_term

def check_condition(user_id, term_id):
    try:
        PatientCondition.get((PatientCondition.patient == user_id) & (PatientCondition.medical_term == term_id))
        return True
    except DoesNotExist:
        return False

def check_prescription(user_id, condition_term_id, prescription_term_id):
    try:
        p = PatientCondition.get((PatientCondition.patient == user_id) & (PatientCondition.medical_term == condition_term_id))
        PatientPrescription.get((PatientPrescription.user_condition == p.id) & (PatientPrescription.medical_term == prescription_term_id))
        return True
    except DoesNotExist:
        return False

### patient medical history ###
def get_history(user_id: int) -> dict:
    patient_conditions = PatientCondition.select().where(PatientCondition.patient == user_id)
    condition_list = []

    for patient_condition in patient_conditions:
        condition_term_id = patient_condition.medical_term.id
        condition_term_info = get_term(condition_term_id, patient_condition.patient.language_code)

        patient_prescriptions = PatientPrescription.select().where(PatientPrescription.user_condition == condition_term_id)
        prescription_list = []

        for patient_prescription in patient_prescriptions:
            prescription_term_id = patient_prescription.medical_term.id
            prescription_info = get_term(prescription_term_id, patient_condition.patient.language_code)

            prescription = {
                "userPrescriptionId": patient_prescription.id,
                "medicalTerm": prescription_info,
                "dosage": patient_prescription.dosage,
                "prescriptionDate": patient_prescription.prescription_date
            }

            prescription_list.append(prescription)

        condition = {
            "userConditionId": condition_term_id,
            "medicalTerm": condition_term_info,
            "status": patient_condition.status,
            "diagnosisDate": patient_condition.diagnosis_date,
            "prescriptions": prescription_list
        }

        condition_list.append(condition)

    ret = {
        "userId": user_id,
        "medicalConditions": condition_list
    }

    return ret

def add_condition(user_id: int, term_id: int, condition_info: dict):
    new_condition = PatientCondition.create(
        medical_term=term_id,
        patient=user_id,
        status=condition_info.get('status'),
        diagnosis_date=condition_info.get('diagnosis_date'),
    )
    new_condition.save()

def update_condition(user_id: int, term_id: int, condition_info: dict):
    condition = PatientCondition.get(PatientCondition.medical_term == term_id, PatientCondition.patient == user_id)

    if 'status' in condition_info:
        condition.status = condition_info.get('status')

    if 'diagnosis_date' in condition_info:
        condition.diagnosis_date = condition_info.get('diagnosis_date')

    condition.save()
    return condition

def delete_condition(user_id: int, term_id: int, condition_info: dict):
    condition = PatientCondition.get(PatientCondition.medical_term == term_id, PatientCondition.patient == user_id)
    condition.delete_instance()
    return

def add_prescription(user_id: int, condition_term_id: int, prescription_term_id: int, prescription_info: dict):
    p = PatientCondition.get((PatientCondition.patient == user_id) & (PatientCondition.medical_term == condition_term_id))

    new_prescription = PatientPrescription.create(
        user_condition=p.id,
        medical_term=prescription_term_id,
        dosage=prescription_info.get('dosage'),
        prescription_date=prescription_info.get('prescription_date')
    )

    new_prescription.save()

def update_prescription(user_id: int, condition_term_id: int, prescription_term_id: int, prescription_info: dict):
    prescription = PatientPrescription.get(PatientPrescription.user_condition == condition_term_id, PatientPrescription.medical_term == prescription_term_id)

    if 'dosage' in prescription_info:
        prescription.dosage = prescription_info.get('dosage')

    if 'prescription_date' in prescription_info:
        prescription.prescription_date = prescription_info.get('prescription_date')

    prescription.save()
    return prescription

def delete_prescription(user_id: int, condition_term_id: int, prescription_term_id: int, prescription_info: dict):
    prescription = PatientPrescription.get(PatientPrescription.user_condition == condition_term_id, PatientPrescription.medical_term == prescription_term_id)
    prescription.delete_instance()
    return
