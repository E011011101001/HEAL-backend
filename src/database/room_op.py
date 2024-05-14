from peewee import DoesNotExist
from datetime import datetime

from .data_models import Room, DoctorInRoom
from .user_ops import get_user_full

def check_room(roomId):
    try:
        Room.get(Room.id == roomId)
        return True
    except DoesNotExist:
        return False

def create_room(userId):
    newRoom = Room.create(
        Patient_id = userId, #check whether userId is patient
        Creation_time = datetime.now()
    )
    newRoom.save()

    return newRoom.id

def get_room(roomId):
    baseRoom = Room.get(baseRoom.id == roomId)
    participantList = []

    # get patient data
    patient = get_user_full(baseRoom.Patient_id)
    participantList.append(patient)

    # get doctor data (n >= 0)
    baseDoctorsInRoom = DoctorInRoom.select().where(baseDoctorsInRoom.Room_id == baseRoom.id)

    for doctorsInRoom in baseDoctorsInRoom:
        doctor = get_user_full(doctorsInRoom.Doctor_id)
        participantList.append(doctor)

    ret = {
        "roomId": baseRoom.id,
        "roomName": "",
        "creationTime": baseRoom.Creation_time,
        "participants": participantList
    }

    return ret

def participant_room(userId, roomId):

    newDoctorInRoom = DoctorInRoom.create(
        Doctor_id = userId,
        Room_id = roomId,
        Joined_time = datetime.now(),
        Enabled = True
    )
    newDoctorInRoom.save()

def get_rooms_all(userId):
    baseRooms = Room.select().where(baseRooms.Patient_id == userId)
    rooms = []

    for baseRoom in baseRooms:
        room = get_room(baseRoom.id)
        rooms.append(room)

    return {"rooms": rooms}
