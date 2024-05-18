# src/database/condoition.py
from peewee import DoesNotExist
from datetime import datetime

from .data_models import PatientCondition, PatientPrescription
from .message_op import get_term


def check_condition(patient_id, medical_term_id):
    """
    Check if a condition already exists for a patient.

    Parameters:
    patient_id (int): ID of the patient
    medical_term_id (int): ID of the medical term

    Returns:
    bool: True if the condition exists, False otherwise
    """
    try:
        PatientCondition.get((PatientCondition.patient == patient_id) & (PatientCondition.medical_term == medical_term_id))
        return True
    except DoesNotExist:
        return False


def check_prescription(condition_id, medical_term_id):
    """
    Check if a prescription already exists for a condition.

    Parameters:
    condition_id (int): ID of the condition
    medical_term_id (int): ID of the medical term

    Returns:
    bool: True if the prescription exists, False otherwise
    """
    try:
        PatientPrescription.get((PatientPrescription.user_condition == condition_id) & (PatientPrescription.medical_term == medical_term_id))
        return True
    except DoesNotExist:
        return False


def get_history(patient_id: int) -> dict:
    """
    Get the medical history of a patient.

    Parameters:
    patient_id (int): ID of the patient

    Returns:
    dict: Medical history of the patient
    """
    patient_conditions = PatientCondition.select().where(PatientCondition.patient == patient_id)
    condition_list = []

    for patient_condition in patient_conditions:
        condition_term_id = patient_condition.medical_term.id
        condition_term_info = get_term(condition_term_id, patient_condition.patient.base_user.language_code)

        patient_prescriptions = PatientPrescription.select().where(PatientPrescription.user_condition == patient_condition.id)
        prescription_list = []

        for patient_prescription in patient_prescriptions:
            prescription_term_id = patient_prescription.medical_term.id
            prescription_info = get_term(prescription_term_id, patient_condition.patient.base_user.language_code)

            prescription = {
                "userPrescriptionId": patient_prescription.id,
                "medicalTerm": prescription_info,
                "dosage": patient_prescription.dosage,
                "prescriptionDate": patient_prescription.prescription_date,
                "frequency": patient_prescription.frequency
            }

            prescription_list.append(prescription)

        condition = {
            "userConditionId": patient_condition.id,
            "medicalTerm": condition_term_info,
            "status": patient_condition.status,
            "diagnosisDate": patient_condition.diagnosis_date,
            "resolutionDate": patient_condition.resolution_date,
            "prescriptions": prescription_list
        }

        condition_list.append(condition)

    return {
        "userId": patient_id,
        "medicalConditions": condition_list
    }


def add_condition(patient_id: int, medical_term_id: int, condition_info: dict):
    """
    Add a new condition for a patient.

    Parameters:
    patient_id (int): ID of the patient
    medical_term_id (int): ID of the medical term
    condition_info (dict): Information about the condition

    Example:
    {
        "status": "current",
        "diagnosis_date": "2022-01-01",
        "resolution_date": "2022-02-01"  # Optional
    }
    """
    new_condition = PatientCondition.create(
        medical_term=medical_term_id,
        patient=patient_id,
        status=condition_info.get('status'),
        diagnosis_date=condition_info.get('diagnosis_date'),
        resolution_date=condition_info.get('resolution_date')
    )
    new_condition.save()


def update_condition(condition_id: int, medical_term_id: int, condition_info: dict, language_code: str):
    """
    Update a patient's condition.

    Parameters:
    condition_id (int): ID of the condition
    medical_term_id (int): ID of the medical term
    condition_info (dict): Updated information about the condition
    language_code (str): Language code for the response

    Example:
    {
        "status": "resolved",
        "diagnosis_date": "2022-01-01",
        "resolution_date": "2022-02-01"  # Optional
    }

    Returns:
    dict: Updated medical history of the patient
    """
    condition = PatientCondition.get(PatientCondition.id == condition_id)

    if 'status' in condition_info:
        condition.status = condition_info.get('status')

    if 'diagnosis_date' in condition_info:
        condition.diagnosis_date = condition_info.get('diagnosis_date')

    if 'resolution_date' in condition_info:
        condition.resolution_date = condition_info.get('resolution_date')

    condition.save()
    return get_history(condition.patient.base_user_id)


def delete_condition(condition_id: int):
    """
    Delete a patient's condition.

    Parameters:
    condition_id (int): ID of the condition
    """
    condition = PatientCondition.get(PatientCondition.id == condition_id)
    condition.delete_instance()


def add_prescription(user_id: int, condition_id: int, medical_term_id: int, prescription_info: dict):
    """
    Add a new prescription for a condition.

    Parameters:
    user_id (int): ID of the doctor
    condition_id (int): ID of the condition
    medical_term_id (int): ID of the medical term
    prescription_info (dict): Information about the prescription

    Example:
    {
        "dosage": "500mg",
        "prescription_date": "2023-01-01T12:00:00",
        "frequency": "twice a day"
    }
    """
    new_prescription = PatientPrescription.create(
        user_condition=condition_id,
        medical_term=medical_term_id,
        dosage=prescription_info.get('dosage'),
        prescription_date=prescription_info.get('prescription_date'),
        frequency=prescription_info.get('frequency')
    )
    new_prescription.save()


def update_prescription(prescription_id: int, prescription_info: dict):
    """
    Update a prescription for a condition.

    Parameters:
    prescription_id (int): ID of the prescription
    prescription_info (dict): Updated information about the prescription

    Example:
    {
        "dosage": "1000mg",
        "prescription_date": "2023-01-01T12:00:00",
        "frequency": "once a day"
    }

    Returns:
    dict: Updated medical history of the patient
    """
    prescription = PatientPrescription.get(PatientPrescription.id == prescription_id)

    if 'dosage' in prescription_info:
        prescription.dosage = prescription_info.get('dosage')

    if 'prescription_date' in prescription_info:
        prescription.prescription_date = prescription_info.get('prescription_date')

    if 'frequency' in prescription_info:
        prescription.frequency = prescription_info.get('frequency')

    prescription.save()
    return get_history(prescription.user_condition.patient.base_user_id)


def delete_prescription(prescription_id: int):
    """
    Delete a prescription for a condition.

    Parameters:
    prescription_id (int): ID of the prescription
    """
    prescription = PatientPrescription.get(PatientPrescription.id == prescription_id)
    prescription.delete_instance()