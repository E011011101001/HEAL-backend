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
        Patient_id = userId,
        Creation_time = datetime.now()
    )
    newRoom.save()

    return newRoom.id

def get_room(roomId):
    room = Room.get(Room.id == roomId)
    participantList = []

    # get patient data
    patient = get_user_full(room.Patient_id)
    participantList.append(patient)

    # get doctor data (n >= 0)
    doctorsInRoom = DoctorInRoom.select().where(DoctorInRoom.Room_id == room.id)

    for doctorInRoom in doctorsInRoom:
        doctor = get_user_full(doctorInRoom.Doctor_id)
        participantList.append(doctor)

    ret = {
        "roomId": room.id,
        "roomName": "",
        "creationTime": room.Creation_time,
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
    rooms = Room.select().where(Room.Patient_id == userId)
    roomlist = []

    for room in rooms:
        roomData = get_room(room.id)
        roomlist.append(roomData)

    return {"rooms": roomlist}

# delete room corresponding to room id
def delete_room(roomId: int):
    room = Room.get(Room.id == roomId)
    room.delete_instance()
    return
