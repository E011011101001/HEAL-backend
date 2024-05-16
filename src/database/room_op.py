from peewee import DoesNotExist
from datetime import datetime

from .data_models import Room, DoctorInRoom
from .user_op import get_user_full

def check_room(room_id):
    try:
        Room.get(Room.id == room_id)
        return True
    except DoesNotExist:
        return False

def create_room(user_id):
    new_room = Room.create(
        patient=user_id,
        creation_time=datetime.now()
    )
    new_room.save()

    return new_room.id

def get_room(room_id):
    room = Room.get(Room.id == room_id)
    participant_list = []

    # get patient data
    patient = get_user_full(room.patient.base_user_id)
    participant_list.append(patient)

    # get doctor data (n >= 0)
    doctors_in_room = DoctorInRoom.select().where(DoctorInRoom.room == room.id)

    for doctor_in_room in doctors_in_room:
        doctor = get_user_full(doctor_in_room.doctor.base_user_id)
        participant_list.append(doctor)

    ret = {
        "roomId": room.id,
        "roomName": "",
        "creationTime": room.creation_time,
        "participants": participant_list
    }

    return ret

def participant_room(user_id, room_id):
    new_doctor_in_room = DoctorInRoom.create(
        doctor=user_id,
        room=room_id,
        joined_time=datetime.now(),
        enabled=True
    )
    new_doctor_in_room.save()

def get_rooms_all(user_id) -> dict:
    rooms = Room.select().where(Room.patient == user_id)
    room_list = []

    for room in rooms:
        room_data = get_room(room.id)
        room_list.append(room_data)

    return {"rooms": room_list}

# delete room corresponding to room id
def delete_room(room_id: int):
    room = Room.get(Room.id == room_id)
    room.delete_instance()
    return
