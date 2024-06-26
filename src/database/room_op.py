# src/database/room_op.py
from peewee import DoesNotExist, JOIN, fn
from datetime import datetime

from .data_models import Room, DoctorInRoom, SecondOpinionRequest, BaseUser
from .user_op import get_user_full


def check_room(room_id):
    """
    Check if a room exists.

    Parameters:
    room_id (int): ID of the room

    Returns:
    bool: True if the room exists, False otherwise
    """
    try:
        Room.get(Room.id == room_id)
        return True
    except DoesNotExist:
        return False


def create_room(user_id):
    """
    Create a new room.

    Parameters:
    user_id (int): ID of the patient creating the room

    Returns:
    int: ID of the newly created room
    """
    new_room = Room.create(
        patient=user_id,
        creation_time=datetime.now()
    )
    new_room.save()
    return new_room.id


def get_room(room_id):
    """
    Get details of a room.

    Parameters:
    room_id (int): ID of the room

    Returns:
    dict: Details of the room including participants
    """
    room = Room.get(Room.id == room_id)
    participant_list = []

    patient = get_user_full(room.patient.base_user_id)
    participant_list.append(patient)

    doctors_in_room = DoctorInRoom.select().where(DoctorInRoom.room == room.id)

    for doctor_in_room in doctors_in_room:
        doctor = get_user_full(doctor_in_room.doctor.base_user_id)
        participant_list.append(doctor)

    return {
        "roomId": room.id,
        "roomName": "",
        "creationTime": room.creation_time,
        "participants": participant_list
    }


def participant_room(user_id, room_id):
    """
    Add a doctor to a room.

    Parameters:
    user_id (int): ID of the doctor
    room_id (int): ID of the room

    Returns:
    bool: True if the doctor was added, False if already in the room
    """
    existing_entry = DoctorInRoom.select().where((DoctorInRoom.doctor == user_id) & (DoctorInRoom.room == room_id)).first()
    if existing_entry:
        return False

    new_doctor_in_room = DoctorInRoom.create(
        doctor=user_id,
        room=room_id,
        joined_time=datetime.now(),
        enabled=True
    )
    new_doctor_in_room.save()
    return True


def leave_room(user_id, room_id):
    """
    Remove a doctor from a room.

    Parameters:
    user_id (int): ID of the doctor
    room_id (int): ID of the room

    Returns:
    bool: True if the doctor was removed, False otherwise
    """
    try:
        doctor_in_room = DoctorInRoom.get((DoctorInRoom.doctor == user_id) & (DoctorInRoom.room == room_id))
        doctor_in_room.delete_instance()
        return True
    except DoesNotExist:
        return False


def get_rooms_all_fixed(user_id) -> dict:
    """
    Get all rooms for a patient.

    Parameters:
    user_id (int): ID of the user

    Returns:
    dict: List of rooms
    """
    user = BaseUser.get(BaseUser.id == user_id)

    room_list = []

    if user.user_type == 1:  # Patient
        rooms = Room.select().where(Room.patient == user_id)
    elif user.user_type == 2:  # Doctor
        rooms = Room.select().join(DoctorInRoom).where(DoctorInRoom.doctor == user_id)
    else:
        return {"rooms": room_list}

    for room in rooms:
        room_data = get_room(room.id)
        room_list.append(room_data)

    return {"rooms": room_list}

def get_rooms_all(user_id) -> dict:
    """
    Get all rooms for a patient.

    Parameters:
    user_id (int): ID of the user

    Returns:
    dict: List of rooms
    """
    rooms = Room.select().where(Room.patient == user_id)
    room_list = []

    for room in rooms:
        room_data = get_room(room.id)
        room_list.append(room_data)

    return {"rooms": room_list}

def get_room_requests_all(user_id) -> dict:
    """
    Get all room requests for doctor to join.

    Parameters:
    user_id (int): ID of the doctor

    Returns:
    dict: List of rooms
    """
    rooms = Room.select().where(
        (Room.doctor.contains(user_id))&
         ((Room.patients.count() == 1)&
          ((Room.doctor.count() == 1) | (Room.doctor.count() == 3))))
    room_list = []

    for room in rooms:
        room_data = get_room(room.id)
        room_list.append(room_data)

    return {"rooms": room_list}

def delete_room(room_id: int):
    """
    Delete a room.

    Parameters:
    room_id (int): ID of the room
    """
    room = Room.get(Room.id == room_id)
    room.delete_instance()


def get_room_doctor_ids(roomId: int) -> list[int]:
    """
    :return: All the active doctor's ids in a room. If none active, return []
    """

    doctors = DoctorInRoom.select().where(DoctorInRoom.room == roomId)
    return [doctor.doctor_id for doctor in doctors]

def get_step1_rooms():
    """
    Get all rooms that only have a patient and no doctors.

    Returns:
    list: List of rooms
    """
    active_doctors_rooms = (DoctorInRoom
                            .select(DoctorInRoom.room)
                            .where(DoctorInRoom.enabled == True)
                            .distinct())

    # Main query to select rooms that are not in the list of rooms with active doctors
    rooms_with_no_doctors = (Room
                             .select()
                             .where(Room.id.not_in(active_doctors_rooms)))

    # Fetch full room details using an existing function assumed to fetch detailed room information
    room_list = []
    for room in rooms_with_no_doctors:
        room_data = get_room(room.id)
        room_list.append(room_data)

    return room_list

def get_step2_rooms(doctor_id):
    """
    Get all rooms that a doctor has joined.

    Parameters:
    doctor_id (int): ID of the doctor

    Returns:
    list: List of rooms
    """
    # Query to find all rooms that the doctor has joined
    rooms_joined = (DoctorInRoom
                    .select(DoctorInRoom.room)
                    .where((DoctorInRoom.doctor == doctor_id) & (DoctorInRoom.enabled == True)))

    # Fetch full room details using an assumed function `get_room` for fetching detailed room information
    room_list = []
    for doctor_in_room in rooms_joined:
        room_data = get_room(doctor_in_room.room.id)
        room_list.append(room_data)

    return room_list

def get_step3_rooms(doctor_id):
    """
    Get all rooms that a doctor has not joined but includes their user_id in the second_opinion_doctor field.

    Parameters:
    doctor_id (int): ID of the doctor

    Returns:
    list: List of rooms
    """
    # Subquery to find rooms that the doctor has joined
    joined_rooms = (DoctorInRoom
                    .select(DoctorInRoom.room)
                    .where(DoctorInRoom.doctor == doctor_id))

    # Main query to select rooms where there is a second opinion request for this doctor and the doctor hasn't joined the room
    target_rooms = (Room
                    .select()
                    .join(SecondOpinionRequest, on=(Room.id == SecondOpinionRequest.room))
                    .where((SecondOpinionRequest.second_opinion_doctor == doctor_id) &
                           (Room.id.not_in(joined_rooms))))

    # Fetch full room details using an assumed function `get_room` for fetching detailed room information
    room_list = []
    for room in target_rooms:
        room_data = get_room(room.id)
        room_list.append(room_data)

    return room_list
