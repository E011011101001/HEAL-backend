# data_seed.py
from datetime import datetime, date

from ..utils import salted_hash, gen_session_token

def seed_data(BaseUser, Doctor, Patient, Room, DoctorInRoom, MedicalTerm, MedicalTermSynonym, MedicalTermTranslation, Message, MessageTermCache):
    # Create Users
    patient_user = BaseUser.create(
        Email="test@gmail.com",
        Password=salted_hash("password"),
        Language_code="en",
        Name="John Doe",
        Type=1,  # PATIENT
        Date_of_birth=date(1990, 12, 25)
    )

    doctor_user_1 = BaseUser.create(
        Email="doctor@gmail.com",
        Password=salted_hash("password"),
        Language_code="jp",
        Name="Dr. Smith",
        Type=2,  # DOCTOR
        Date_of_birth=date(1980, 2, 15)
    )

    doctor_user_2 = BaseUser.create(
        Email="english_doctor@gmail.com",
        Password=salted_hash("password"),
        Language_code="en",
        Name="Dr. Jones",
        Type=2,  # DOCTOR
        Date_of_birth=date(1985, 5, 10)
    )

    # Create Patients
    Patient.create(
        BaseUser_id=patient_user.id,
        Height=190,
        Weight=115
    )

    # Create Doctors
    Doctor.create(
        BaseUser_id=doctor_user_1.id,
        Specialisation="Cardiology",
        Hospital="Kyoto University Hospital"
    )

    Doctor.create(
        BaseUser_id=doctor_user_2.id,
        Specialisation="Cardiology",
        Hospital="St Pauls Hospital"
    )

    # Create Medical Term
    medical_term = MedicalTerm.create(
        MedicalTerm_type="CONDITION"
    )

    # Add Synonyms
    synonyms = ["COVID", "COVID-19", "Corona", "COVID 19", "コロナ"]
    for synonym in synonyms:
        MedicalTermSynonym.create(
            MedicalTerm_id=medical_term.id,
            Synonym=synonym
        )

    MedicalTermTranslation.create(
        MedicalTerm_id=medical_term.id,
        Language_code="en",
        Name="COVID-19",
        Description="COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
        URL="https://www.nhs.uk/conditions/coronavirus-covid-19/"
    )
    
    MedicalTermTranslation.create(
        MedicalTerm_id=medical_term.id,
        Language_code="jp",
        Name="コロナウイルス",
        Description="COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
        URL="https://www3.nhk.or.jp/nhkworld/en/news/tags/82/"
    )

    # Create Room
    room = Room.create(
        Patient_id=patient_user.id,
        Creation_time=datetime.now()
    )

    # Create Doctor in Room
    DoctorInRoom.create(
        Doctor_id=doctor_user_1.id,
        Room_id=room.id,
        Joined_time=datetime.now(),
        Enabled=True
    )

    DoctorInRoom.create(
        Doctor_id=doctor_user_2.id,
        Room_id=room.id,
        Joined_time=datetime.now(),
        Enabled=True
    )

    # Create Messages
    message_1 = Message.create(
        User_id=patient_user.id,
        Room_id=room.id,
        Text="Hi, I've lost my sense of taste and I'm coughing a lot.",
        Send_time=datetime.now()
    )

    message_2 = Message.create(
        User_id=doctor_user_1.id,
        Room_id=room.id,
        Text="新型コロナウイルス感染症に感染している場合は家にいてください",
        Send_time=datetime.now()
    )

    # Link the medical term to the second message
    MessageTermCache.create(
        MedicalTerm_id=medical_term.id,
        Message_id=message_2.id
    )

    print("Initial data seeded.")
