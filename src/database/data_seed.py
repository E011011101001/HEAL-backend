# data_seed.py
from datetime import datetime, date

def seed_data(BaseUser, Doctor, Patient, Room, DoctorInRoom, MedicalTerm, Message):
    # Create Users
    patient_user = BaseUser.create(
        Email="email@gmail.com",
        Password="hashed_password",
        Language_code="en",
        Name="John Doe",
        Type=1,  # PATIENT
        Date_of_birth=date(1990, 12, 25)
    )

    doctor_user_1 = BaseUser.create(
        Email="doctor@gmail.com",
        Password="hashed_password",
        Language_code="jp",
        Name="Dr. Smith",
        Type=2,  # DOCTOR
        Date_of_birth=date(1980, 2, 15)
    )

    doctor_user_2 = BaseUser.create(
        Email="english_doctor@gmail.com",
        Password="hashed_password",
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
        Term_id="1",
        Discription="COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
        URL="https://www.nhs.uk/conditions/coronavirus-covid-19/"
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
    Message.create(
        User_id=patient_user.id,
        Room_id=room.id,
        Text="Hi, I've lost my sense of taste and I'm coughing a lot.",
        Send_time=datetime.now()
    )

    Message.create(
        User_id=doctor_user_1.id,
        Room_id=room.id,
        Text="新型コロナウイルス感染症に感染している場合は家にいてください",
        Send_time=datetime.now()
    )

    print("Initial data seeded.")