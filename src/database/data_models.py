# All Xxx_id fields will be replaced by just id

import sys

from peewee import SqliteDatabase, Model, AutoField, DateField, DateTimeField, TextField, IntegerField,\
    ForeignKeyField, BooleanField, CompositeKey

from ..glovars import DB_PATH


# pragmas as instructed at https://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField
db = SqliteDatabase(DB_PATH, pragmas=[('foreign_keys', 'on')])

class BaseUser(Model):
    id = AutoField()
    Email = TextField()
    Password = TextField()
    Language_code = TextField(default='en')
    Name = TextField()
    Type = IntegerField() # 1 for Patient, 2 for Doctor. See glovars

    class Meta:
        database = db


class Doctor(Model):
    BaseUser_id = ForeignKeyField(BaseUser, backref='doctor', primary_key=True, on_delete='CASCADE')
    Specialisation = TextField(null=True)
    Hospital = TextField(null=True)

    class Meta:
        database = db


class Patient(Model):
    BaseUser_id = ForeignKeyField(BaseUser, backref='patient', primary_key=True, on_delete='CASCADE')
    Date_of_birth = DateField(null=True)
    Height = IntegerField(null=True)
    Weight = IntegerField(null=True)

    class Meta:
        database = db


class Session(Model):
    id = AutoField()
    User_id = ForeignKeyField(BaseUser, backref='sessions')
    Token = TextField(index=True, unique=True)
    Valid_until = DateTimeField()

    class Meta:
        database = db


class Room(Model):
    id = AutoField()
    Patient_id = ForeignKeyField(Patient, backref='room', null=True)
    Creation_time = DateTimeField()

    class Meta:
        database = db


class DoctorInRoom(Model):
    Doctor_id = ForeignKeyField(Doctor, backref='doctorInRoom')
    Room_id = ForeignKeyField(Room, backref='doctorInRoom')
    Joined_time = DateTimeField()
    Enabled = BooleanField(default=True)

    class Meta:
        database = db
        primary_key = CompositeKey('Doctor_id', 'Room_id', 'Joined_time')


class MedicalTerm(Model):
    id = AutoField()
    Term_id = TextField(index=True)
    Language_code = TextField(default='en', index=True)
    Discription = TextField()
    URL = TextField(null=True)

    class Meta:
        database = db


class PatientCondition(Model):
    id = AutoField()
    MedicalTerm_id = ForeignKeyField(MedicalTerm)
    Patient_id = ForeignKeyField(Patient, backref='patientCondition')
    Status = TextField()
    Diagnosis_date = DateField()
    Resolution_date = DateField(null=True)

    class Meta:
        database = db


class PatientPrescription(Model):
    id = AutoField()
    UserCondition_id = ForeignKeyField(PatientCondition, backref='patientPrescription')
    MedicalTerm_id = ForeignKeyField(MedicalTerm, backref='patientPrescription')
    Dosage = TextField()
    Frequency = TextField()

    class Meta:
        database = db


class Message(Model):
    id = AutoField()
    User_id = ForeignKeyField(BaseUser, backref='message')
    Room_id = ForeignKeyField(Room, backref='message')
    Text = TextField()

    class Meta:
        database = db


class Report(Model):
    id = AutoField()
    Room_id = ForeignKeyField(Room, backref='report')
    Consultation_date = DateField()
    Report_details = TextField()

    class Meta:
        database = db


class MessageTermCache(Model):
    MedicalTerm_id = ForeignKeyField(MedicalTerm, backref='messageTermCache')
    Message_id = ForeignKeyField(Message, backref='messageTermCache')

    class Meta:
        database = db
        primary_key = CompositeKey('MedicalTerm_id', 'Message_id')


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
        PatientCondition,
        PatientPrescription,
        Message,
        Report,
        MessageTermCache
    ])
    db.close()
