# src/database/data_models.py
from peewee import (
    SqliteDatabase, Model, AutoField, DateField, DateTimeField, 
    TextField, IntegerField, ForeignKeyField, BooleanField, CompositeKey
)

from .data_seed import seed_data
from ..glovars import DB_PATH

# Pragmas as instructed at https://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField
db = SqliteDatabase(DB_PATH, pragmas=[('foreign_keys', 'on')])


class BaseUser(Model):
    id = AutoField()
    email = TextField(unique=True)
    password = TextField()
    language_code = TextField(default='en')
    name = TextField()
    user_type = IntegerField()  # 1 for Patient, 2 for Doctor. See glovars
    date_of_birth = DateField(null=True)

    class Meta:
        database = db


class Doctor(Model):
    base_user = ForeignKeyField(BaseUser, backref='doctor', primary_key=True, on_delete='CASCADE')
    specialisation = TextField(null=True)
    hospital = TextField(null=True)

    class Meta:
        database = db


class Patient(Model):
    base_user = ForeignKeyField(BaseUser, backref='patient', primary_key=True, on_delete='CASCADE')
    height = IntegerField(null=True)
    weight = IntegerField(null=True)

    class Meta:
        database = db


class Session(Model):
    id = AutoField()
    user = ForeignKeyField(BaseUser, backref='sessions', on_delete="CASCADE")
    token = TextField(index=True, unique=True)
    valid_until = DateTimeField()

    class Meta:
        database = db


class Room(Model):
    id = AutoField()
    patient = ForeignKeyField(Patient, backref='rooms', null=True, on_delete="CASCADE")
    creation_time = DateTimeField()

    class Meta:
        database = db


class DoctorInRoom(Model):
    doctor = ForeignKeyField(Doctor, backref='doctor_in_rooms', on_delete="CASCADE")
    room = ForeignKeyField(Room, backref='doctor_in_rooms', on_delete="CASCADE")
    joined_time = DateTimeField()
    enabled = BooleanField(default=True)

    class Meta:
        database = db
        primary_key = CompositeKey('doctor', 'room', 'joined_time')


class MedicalTerm(Model):
    id = AutoField()
    term_type = TextField(choices=[('CONDITION', 'CONDITION'), ('PRESCRIPTION', 'PRESCRIPTION'), ('GENERAL', 'GENERAL')], default='GENERAL')

    class Meta:
        database = db


class MedicalTermSynonym(Model):
    id = AutoField()
    medical_term = ForeignKeyField(MedicalTerm, backref='synonyms', on_delete="CASCADE")
    synonym = TextField(index=True)
    language_code = TextField(default='en')

    class Meta:
        database = db


class MedicalTermTranslation(Model):
    medical_term = ForeignKeyField(MedicalTerm, backref='translations', on_delete="CASCADE")
    language_code = TextField(default='en', index=True)
    name = TextField()
    description = TextField()
    url = TextField(null=True)

    class Meta:
        database = db
        primary_key = CompositeKey('medical_term', 'language_code')


class PatientCondition(Model):
    id = AutoField()
    medical_term = ForeignKeyField(MedicalTerm, on_delete="CASCADE")
    patient = ForeignKeyField(Patient, backref='patient_conditions', on_delete="CASCADE")
    status = TextField()
    diagnosis_date = DateField()
    resolution_date = DateField(null=True)

    class Meta:
        database = db


class PatientPrescription(Model):
    id = AutoField()
    user_condition = ForeignKeyField(PatientCondition, backref='patient_prescriptions', on_delete="CASCADE")
    medical_term = ForeignKeyField(MedicalTerm, backref='patient_prescriptions', on_delete="CASCADE")
    dosage = TextField()
    prescription_date = DateTimeField()
    frequency = TextField()

    class Meta:
        database = db


class Message(Model):
    id = AutoField()
    user = ForeignKeyField(BaseUser, backref='messages', on_delete="CASCADE")
    room = ForeignKeyField(Room, backref='messages', on_delete="CASCADE")
    text = TextField()
    send_time = DateTimeField()

    class Meta:
        database = db


class Report(Model):
    id = AutoField()
    room = ForeignKeyField(Room, backref='reports', on_delete="CASCADE")
    consultation_date = DateField()
    report_details = TextField()

    class Meta:
        database = db


class MessageTermCache(Model):
    medical_term = ForeignKeyField(MedicalTerm, backref='message_term_caches', on_delete="CASCADE")
    message = ForeignKeyField(Message, backref='message_term_caches', on_delete="CASCADE")
    original_synonym = ForeignKeyField(MedicalTermSynonym, backref='original_message_term_caches', null=True, on_delete="CASCADE")
    translated_synonym = ForeignKeyField(MedicalTermSynonym, backref='translated_message_term_caches', null=True, on_delete="CASCADE")

    class Meta:
        database = db
        primary_key = CompositeKey('medical_term', 'message')


class MessageTranslationCache(Model):
    message = ForeignKeyField(Message, backref='message_translation_caches', on_delete="CASCADE")
    language_code = TextField(default='en', index=True)
    translated_text = TextField()

    class Meta:
        database = db
        primary_key = CompositeKey('message', 'language_code')


def init():
    db.connect()
    db.create_tables([
        BaseUser,
        Doctor,
        Patient,
        Session,
        Room,
        DoctorInRoom,
        MedicalTerm,
        MedicalTermSynonym,
        MedicalTermTranslation,
        PatientCondition,
        PatientPrescription,
        Message,
        Report,
        MessageTermCache,
        MessageTranslationCache
    ])
    print("Database tables created.")
    seed_data(BaseUser, Doctor, Patient, Room, DoctorInRoom, MedicalTerm, MedicalTermSynonym, MedicalTermTranslation, Message, MessageTermCache, MessageTranslationCache)
    print("Database seeded with initial data.")
    db.close()
