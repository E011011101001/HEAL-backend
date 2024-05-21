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
    synonyms_en_prescription = ["Paracetamol", "Tylenol", "Panadol"]
    synonyms_jp_prescription = ["パラセタモール", "タイレノール", "パナドール"]

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
        language_code="en",
        name="Tylenol",
        description="Tylenol is used as an antipyretic analgesic.",
        url="https://www.webmd.com/drugs/2/drug-7076/tylenol-oral/details"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term.id,
        language_code="en",
        name="Panadol",
        description="Tylenol is used as an antipyretic analgesic.",
        url="https://www.haleonhealthpartner.com/en-ie/pain-relief/brands/panadol/overview/"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term.id,
        language_code="jp",
        name="パラセタモール",
        description="パラセタモールは痛みと発熱を治療するために使用されます。",
        url="https://www.nhs.uk/medicines/paracetamol/"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term.id,
        language_code="jp",
        name="タイレノール",
        description="タイレノールは解熱鎮痛剤として使用されます。",
        url="https://fastdoctor.jp/columns/corona-high-fever"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term.id,
        language_code="jp",
        name="パナドール",
        description="パナドールは解熱鎮痛剤として使用されます。",
        url="https://www.petkusuri.com/products/panadol-500mg"
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

    ###↑ONE CASE ###
    ###ADD INFORMATION###
    #More Patients
    # User 2
    patient_user2 = BaseUser.create(
        email="jane.smith@gmail.com",
        password=salted_hash("password"),
        language_code="en",
        name="Jane Smith",
        user_type=1,  # PATIENT
        date_of_birth=date(1985, 5, 14)
    )
    Patient.create(
        base_user=patient_user2.id,
        height=165,
        weight=70
    )

    # User 3
    patient_user3 = BaseUser.create(
        email="michael.jordan@gmail.com",
        password=salted_hash("password"),
        language_code="en",
        name="Michael Jordan",
        user_type=1,  # PATIENT
        date_of_birth=date(1963, 2, 17)
    )
    Patient.create(
        base_user=patient_user3.id,
        height=198,
        weight=98
    )

    # User 4
    patient_user4 = BaseUser.create(
        email="emily.jones@gmail.com",
        password=salted_hash("password"),
        language_code="en",
        name="Emily Jones",
        user_type=1,  # PATIENT
        date_of_birth=date(1992, 11, 30)
    )
    Patient.create(
        base_user=patient_user4.id,
        height=160,
        weight=55
    )

    # User 5
    patient_user5 = BaseUser.create(
        email="david.wilson@gmail.com",
        password=salted_hash("password"),
        language_code="en",
        name="David Wilson",
        user_type=1,  # PATIENT
        date_of_birth=date(1978, 7, 22)
    )
    Patient.create(
        base_user=patient_user5.id,
        height=175,
        weight=80
    )

    #More Doctors
    doctor_user_4 = BaseUser.create(
    email="pediatrician_doctor@gmail.com",
    password=salted_hash("password"),
    language_code="jp",
    name="Dr. Sato",
    user_type=2,  # DOCTOR
        date_of_birth=date(1980, 3, 15)
    )
    Doctor.create(
        base_user=doctor_user_4.id,
        specialisation="Pediatrics",
        hospital="Tokyo Ikebukuro Hospital"
    )

    doctor_user_5 = BaseUser.create(
        email="oncologist_doctor@gmail.com",
        password=salted_hash("password3"),
        language_code="jp",
        name="Dr. Tanaka",
        user_type=2,  # DOCTOR
        date_of_birth=date(1968, 11, 10)
    )
    Doctor.create(
        base_user=doctor_user_5.id,
        specialisation="Oncology",
        hospital="Kyoto nijo Hospital"
    )

    #Create Medical Term for Condition
    condition_term_2 = MedicalTerm.create(
        term_type="CONDITION"
    )

    # Add Synonyms for Condition
    synonyms_en_2 = ["Asthma", "Bronchial Asthma", "Reactive Airway Disease", "Asthmatic Condition", "Respiratory Asthma"]
    synonyms_jp_2 = ["喘息", "気管支喘息", "呼吸器喘息"]

    for synonym in synonyms_en_2:
        MedicalTermSynonym.create(
            medical_term_2=condition_term_2.id,
            synonym=synonym,
            language_code="en"
        )

    for synonym in synonyms_jp_2:
        MedicalTermSynonym.create(
            medical_term_2=condition_term_2.id,
            synonym=synonym,
            language_code="jp"
        )

    MedicalTermInfo.create(
        medical_term_2=condition_term_2.id,
        language_code="en",
        name="Bronchial Asthma",
        description="Bronchial asthma is a condition where inflammation persists in the airways, causing the airways to become sensitive to various triggers and repeatedly narrowing them in spasms.",
        url="https://my.clevelandclinic.org/health/diseases/6424-asthma"
    )

    MedicalTermInfo.create(
        medical_term_2=condition_term_2.id,
        language_code="jp",
        name="気管支喘息",
        description="気管支喘息は気道に炎症が続き、さまざまな刺激に気道が敏感になって発作的に気道が狭くなることを繰り返す病気です",
        url="https://www.mhlw.go.jp/new-info/kobetu/kenkou/ryumachi/dl/jouhou01-07.pdf"
    )

    # Create Medical Term for Prescription
    prescription_term_2 = MedicalTerm.create(
        term_type="PRESCRIPTION"
    )

    # Add Synonyms for Prescription
    synonyms_en_prescription_2 = ["Relvar", "Salmeterol"]
    synonyms_jp_prescription_2 = ["レルベア", "サルタノール"]

    for synonym in synonyms_en_prescription_2:
        MedicalTermSynonym.create(
            medical_term=prescription_term_2.id,
            synonym=synonym,
            language_code="en"
        )

    for synonym in synonyms_jp_prescription_2:
        MedicalTermSynonym.create(
            medical_term=prescription_term_2.id,
            synonym=synonym,
            language_code="jp"
        )

    MedicalTermInfo.create(
        medical_term=prescription_term_2.id,
        language_code="en",
        name="Relvar",
        description="Lerbea reduces inflammation in the airways and dilates the bronchi, thereby improving cough and breathlessness.",
        url="https://www.rad-ar.or.jp/siori/english/search/result?n=34088"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term_2.id,
        language_code="en",
        name="Salmeterol",
        description="It is used both as a reliever to immediately suppress symptoms during a seizure and as a controller to prevent seizures with daily doses.",
        url="https://medlineplus.gov/druginfo/meds/a695001.html"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term_2.id,
        language_code="jp",
        name="レルベア",
        description="レルベアは気道の炎症を抑え気管支を拡張することで、咳や息苦しさなどを改善する効果があります。",
        url="https://www.kegg.jp/medicus-bin/japic_med?japic_code=00064840"
    )

    MedicalTermInfo.create(
        medical_term=prescription_term_2.id,
        language_code="jp",
        name="サルタノール",
        description="発作の時に即座に症状を抑えるリリーバーとしても、毎日の服用で発作を予防するコントローラーとしても使用されます。",
        url="https://www.kamimutsukawa.com/blog2/kokyuuki/5712/"
    )

    print("Additional data seeded.")

