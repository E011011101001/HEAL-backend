# src/database/data_seed.py
from datetime import datetime, date

from ..utils import salted_hash

def seed_data(BaseUser, Doctor, Patient, Room, DoctorInRoom, SecondOpinionRequest, MedicalTerm,
        MedicalTermSynonym, MedicalTermInfo, Message, MessageTermCache,
        MessageTranslationCache, PatientCondition, PatientPrescription):
    # Create Users
    patient_user = BaseUser.create(
        email="test@gmail.com",
        password=salted_hash("password"),
        language_code="en",
        name="John Doe",
        user_type=1,  # PATIENT
        date_of_birth=date(1990, 12, 25)
    )

    doctor_user_1 = BaseUser.create(
        email="doctor@gmail.com",
        password=salted_hash("password"),
        language_code="jp",
        name="Dr. Smith",
        user_type=2,  # DOCTOR
        date_of_birth=date(1980, 2, 15)
    )

    doctor_user_2 = BaseUser.create(
        email="english_doctor@gmail.com",
        password=salted_hash("password"),
        language_code="en",
        name="Dr. Jones",
        user_type=2,  # DOCTOR
        date_of_birth=date(1985, 5, 10)
    )

    # Create special AI doctor chatbot user
    ai_doctor_user = BaseUser.create(
        id=0,
        email="aidoc@chatbot.com",
        password=salted_hash("password"),
        language_code="en",
        name="AI Doctor Chatbot",
        user_type=2,  # DOCTOR
        date_of_birth=date(2020, 1, 1)  # Arbitrary date of birth
    )

    # Create Patients
    Patient.create(
        base_user=patient_user.id,
        height=190,
        weight=115
    )

    # Create Doctors
    Doctor.create(
        base_user=doctor_user_1.id,
        specialisation="Cardiology",
        hospital="Kyoto University Hospital"
    )

    Doctor.create(
        base_user=doctor_user_2.id,
        specialisation="Cardiology",
        hospital="St Pauls Hospital"
    )

    Doctor.create(
        base_user=ai_doctor_user.id,
        specialisation="General Medicine",
        hospital="Virtual Hospital"
    )

    # Create Medical Term for Condition
    condition_term = MedicalTerm.create(
        term_type="CONDITION"
    )

    # Add Synonyms for Condition
    synonyms_en = ["covid", "covid-19", "corona", "covid 19", "coronavirus"]
    synonyms_jp = ["コロナ", "新型コロナウイルス"]

    for synonym in synonyms_en:
        MedicalTermSynonym.create(
            medical_term=condition_term.id,
            synonym=synonym,
            language_code="en"
        )

    for synonym in synonyms_jp:
        MedicalTermSynonym.create(
            medical_term=condition_term.id,
            synonym=synonym,
            language_code="jp"
        )

    MedicalTermInfo.create(
        medical_term=condition_term.id,
        language_code="en",
        name="COVID-19",
        description="COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
        url="https://www.nhs.uk/conditions/coronavirus-covid-19/"
    )

    MedicalTermInfo.create(
        medical_term=condition_term.id,
        language_code="jp",
        name="コロナウイルス",
        description="COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
        url="https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
    )

    # Create Medical Term for Prescription
    prescription_term = MedicalTerm.create(
        term_type="PRESCRIPTION"
    )

    # Add Synonyms for Prescription
    synonyms_en_prescription = ["paracetamol", "acetaminophen", "tylenol", "panadol"]
    synonyms_jp_prescription = ["パラセタモール", "アセトアミノフェン", "タイレノール", "パナドール"]

    for synonym in synonyms_en_prescription:
        MedicalTermSynonym.create(
            medical_term=prescription_term.id,
            synonym=synonym,
            language_code="en"
        )

    for synonym in synonyms_jp_prescription:
        MedicalTermSynonym.create(
            medical_term=prescription_term.id,
            synonym=synonym,
            language_code="jp"
        )

    MedicalTermInfo.create(
        medical_term=prescription_term.id,
        language_code="en",
        name="Paracetamol",
        description="Paracetamol is used to treat pain and fever.",
        url="https://www.nhs.uk/medicines/paracetamol/"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term.id,
        language_code="jp",
        name="パラセタモール",
        description="パラセタモールは痛みと発熱を治療するために使用されます。",
        url="https://www.nhs.uk/medicines/paracetamol/"
    )

    # Create Room
    room = Room.create(
        patient=patient_user.id,
        creation_time=datetime.now()
    )

    # Create Doctor in Room
    DoctorInRoom.create(
        doctor=doctor_user_1.id,
        room=room.id,
        joined_time=datetime.now(),
        enabled=True
    )

    DoctorInRoom.create(
        doctor=doctor_user_2.id,
        room=room.id,
        joined_time=datetime.now(),
        enabled=True
    )

    # Create Messages
    message_1 = Message.create(
        user=patient_user.id,
        room=room.id,
        text="Hi, I've lost my sense of taste and I'm coughing a lot.",
        send_time=datetime.now()
    )

    message_2 = Message.create(
        user=doctor_user_1.id,
        room=room.id,
        text="新型コロナウイルス感染症に感染している場合は家にいてください",
        send_time=datetime.now()
    )

    # Link the medical term to the second message
    MessageTermCache.create(
        medical_term=condition_term.id,
        message=message_2.id,
        original_synonym=MedicalTermSynonym.get(MedicalTermSynonym.synonym == "新型コロナウイルス").id,
        translated_synonym=MedicalTermSynonym.get(MedicalTermSynonym.synonym == "coronavirus").id
    )

    # Add Translations for Messages
    MessageTranslationCache.create(
        message=message_1.id,
        language_code="jp",
        translated_text="こんにちは、味覚がなくなり、たくさん咳をしています。"
    )

    MessageTranslationCache.create(
        message=message_2.id,
        language_code="en",
        translated_text="Please stay home if you have been infected with the novel coronavirus."
    )

    # Create Patient Condition for COVID-19
    patient_condition = PatientCondition.create(
        medical_term=condition_term.id,
        patient=patient_user.id,
        status="current",
        diagnosis_date=date(2022, 1, 1)
    )

    # Create Prescription for the COVID-19 Condition
    PatientPrescription.create(
        user_condition=patient_condition.id,
        medical_term=prescription_term.id,
        dosage="500mg",
        prescription_date=datetime.now(),
        frequency="twice a day"
    )

    print("Initial data seeded.")

    # More Doctors
    doctor_user_3 = BaseUser.create(
        email="cardio_doctor@gmail.com",
        password=salted_hash("password"),
        language_code="jp",
        name="Dr. Hiro",
        user_type=2,  # DOCTOR
        date_of_birth=date(1975, 8, 20)
    )

    Doctor.create(
        base_user=doctor_user_3.id,
        specialisation="Neurology",
        hospital="Osaka Medical Center"
    )

    # New Room without any doctor joined
    room2 = Room.create(
        patient=patient_user.id,
        creation_time=datetime.now()
    )

    # New Room with one doctor
    room3 = Room.create(
        patient=patient_user.id,
        creation_time=datetime.now()
    )

    DoctorInRoom.create(
        doctor=doctor_user_3.id,
        room=room3.id,
        joined_time=datetime.now(),
        enabled=True
    )

    # Second Opinion Request targeting a doctor who hasn't joined yet
    SecondOpinionRequest.create(
        room=room3.id,
        requesting_doctor=doctor_user_1.id,
        second_opinion_doctor=doctor_user_2.id
    )

    # Messages for the new rooms
    Message.create(
        user=patient_user.id,
        room=room2.id,
        text="I feel dizzy and have headaches.",
        send_time=datetime.now()
    )

    Message.create(
        user=doctor_user_3.id,
        room=room3.id,
        text="It seems like you might need a neurology consult.",
        send_time=datetime.now()
    )

    print("Additional data seeded.")
