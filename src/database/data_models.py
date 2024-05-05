# All Xxx_id fields will be replaced by just id

import sys

from peewee import SqliteDatabase, Model, AutoField, DateField, DateTimeField, TextField, IntegerField, ForeignKeyField

from ..glovars import DB_PATH, PATIENT, DOCTOR


# pragmas as instructed at https://docs.peewee-orm.com/en/latest/peewee/api.html#AutoField
db = SqliteDatabase(DB_PATH, pragmas=[('foreign_keys', 'on')])

class User(Model):
    id = AutoField()
    Email = TextField()
    Language_code = TextField(default='en')
    Name = TextField()
    Type = IntegerField() # 1 for Patient, 2 for Doctor. See glovars

    #PATIENT only
    Date_of_birth = DateField(null=True)
    Height = IntegerField(null = True)
    Weight = IntegerField(null = True)

    # DOCTOR only
    Hospital = TextField(null = True)
    Specialisation = TextField(null = True)

    class Meta:
        database = db


class Session(Model):
    id = AutoField()
    User_id = ForeignKeyField(User, backref='user')
    Token = TextField(index=True, unique=True)
    Valid_until = DateTimeField()

    class Meta:
        database = db


def init():
    db.connect()
    db.create_tables([User, Session])
    db.close()
