# All Xxx_id fields will be replaced by just id

import sys

from peewee import SqliteDatabase, Model, AutoField, DateField, DateTimeField, TextField, IntegerField, ForeignKeyField

from ..glovars import DB_PATH


# pragmas as instructed at https://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField
db = SqliteDatabase(DB_PATH, pragmas=[('foreign_keys', 'on')])

class BaseUser(Model):
    id = AutoField()
    Email = TextField()
    Language_code = TextField(default='en')
    Name = TextField()
    Type = IntegerField() # 1 for Patient, 2 for Doctor. See glovars

    class Meta:
        database = db

class Session(Model):
    id = AutoField()
    User_id = ForeignKeyField(BaseUser, backref='sessions')
    Token = TextField(index=True, unique=True)
    Valid_until = DateTimeField()

    class Meta:
        database = db

class Doctor(Model):
    BaseUser_id = ForeignKeyField(BaseUser, backref='doctor', index = True, null = True, unique = True)
    Specialisation = TextField(null = True)
    Hospital = TextField(null = True)

    class Meta:
        database = db

class DoctorInRoom(Model):
    id = ForeignKeyField(Doctor, backref='doctorinroom', index = True)
    Room_id = AutoField()
    Joined_time = DateTimeField()
    Enabled = bool()

    class Meta:
        database = db

class Patient(Model):
    BaseUser_id = ForeignKeyField(BaseUser, backref='patient', index = True, null = True, unique = True)
    Date_of_birth = DateField(null = True)
    Height = IntegerField(null = True)
    Weight = IntegerField(null = True)

    class Meta:
        database = db

class PatientCondition(Model):
    id = AutoField()
    Patient_id = ForeignKeyField(Patient, backref='patientcondition', null = True)
    Status = TextField()
    Diagnosis_date = DateField()
    Resolution_date = DateField(null = True)

    class Meta:
        database = db

class PatientPrescription(Model):
    UserCondition_id = ForeignKeyField(PatientCondition, backref='patientprescription')
    Dosage = TextField()
    Frequency = TextField()

    class Meta:
        database = db


class Room(Model):
    id = AutoField()
    Patient_id = ForeignKeyField(Patient, backref='room', null = True)
    Creation_time = DateTimeField()

    class Meta:
        database = db

class Message(Model):
    id = AutoField()
    User_id = ForeignKeyField(BaseUser, backref='message')
    Room_id = ForeignKeyField(Room, backref='message')
    Text = TextField(null = True)

    class Meta:
        database = db

class Report(Model):
    id = AutoField()
    Room_id = ForeignKeyField(Room, backref='report')
    Consultation = DateField()
    Report_details = TextField()

    class Meta:
        database = db


class MedicalTerm(Model):
    id = TextField(index = True)
    Term_id = AutoField()
    Language_code = TextField(default='en')
    Discription = TextField()

    class Meta:
        database = db


class MedicalTeamLink(Model):
    Link_id = AutoField()
    URL = TextField()
    MedicalTerm_id = ForeignKeyField(MedicalTerm, backref='medicaltermlink')

    class Meta:
        database = db




def init():
    db.connect()
    db.create_tables([BaseUser, Session])
    db.close()
