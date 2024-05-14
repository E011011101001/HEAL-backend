### user ###
from peewee import DoesNotExist
from datetime import datetime, timedelta

from .data_models import BaseUser, Doctor, Patient, Session
from ..utils import salted_hash, gen_session_token
from ..glovars import PATIENT, DOCTOR
from .user_ops import get_user_full

'''
update user details

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-37d7339d-15c4-41a7-91ce-4ee009dbe0b4
'''
def update_user(userId: int, userUpdateInfo: dict):
    # get user with userid from database
    baseUser = BaseUser.get(BaseUser.id == userId)

    # update parts of user we need to
    if 'name' in userUpdateInfo:
        baseUser.Name = userUpdateInfo.get('name')

    if 'email' in userUpdateInfo:
        baseUser.Email = userUpdateInfo.get('email')

    if 'language' in userUpdateInfo:
        baseUser.Language = userUpdateInfo.get('language')

    # HANDLE PATIENT/DOCTOR - currently broken
    if baseUser.Type == PATIENT:
        patient = baseUser.patient[0]
        if 'date0fBirth' in userUpdateInfo:
            patient.Date0fBirth = userUpdateInfo.get('date0fBirth')
        if 'height' in userUpdateInfo:
            patient.Height = userUpdateInfo.get('height')
        if 'weight' in userUpdateInfo:
            patient.Weight = userUpdateInfo.get('weight')
        patient.save()
    else:
        doctor = baseUser.doctor[0]
        if 'hostpial' in userUpdateInfo:
            doctor.Hostpial = userUpdateInfo.get('hostpial')
        if 'specialisation' in userUpdateInfo:
            doctor.Specialisation = userUpdateInfo.get('specialisation')
        doctor.save()

    # save user back to database
    baseUser.save()

    return baseUser

# delete user information
def delete_user(userId: int):
    baseUser = BaseUser.get(BaseUser.id == userId)
    baseUser.delete_instance()
    return


### chat room ###
# create new chat room
def create_room_id():
    pass

'''
get room details from room id

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-3c1ed2f2-a82a-407a-a3f2-6dc3e597eddf
'''
def get_room_details(roomId: int) -> dict:
    pass

# delete room corresponding to room id
def delete_room(roomId: int):
    pass

'''
add user information to participants in designated room

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-ade50e58-403e-4f32-bef3-5dc57e06fd9e
'''
def participant_room(roomId: int, userId: int) -> dict:
    pass

'''
remove user from participants and return room details

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-4a9199ea-3a21-42f6-afa5-7f2b3a0c1875
'''
def exit_room(roomId: int, userId: int) -> dict:
    pass

'''
get rooms user participants

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-16aebfc5-f0c6-44b5-bf4f-b9e9117def53
'''
def get_participanting_rooms(userId: int) -> dict:
    pass


### chat message ###
'''
get all messages in designated room and divide into pages

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-0377a979-31f6-4908-b5db-6a39036023b8
'''
def get_chat_messages(roomId: int, pageNum: int, limNum: int) -> dict:
    pass

'''
get a message from room id and message id

reference
https://www.postman.com/winter-capsule-599080/workspace/heal/request/1136812-e04a3e92-bb53-45f4-b557-e1fdaa52ec7a
'''
def get_message(roomId: int, messageId: int) -> dict:
    pass

### medical term ###
def create_term(termInfo: dict) -> dict:
    pass

def get_terms() -> dict:
    pass

def get_single_term(termId: int) -> dict:
    pass

def update_term(termId: int) -> dict:
    pass

def delete_term(termId: int):
    pass

### link between message and term ###
def get_linking_term(messageId: int) -> dict:
    pass

def create_linking_term(messageId: int, termId: int) -> dict:
    pass

def delete_linking_term(messageId: int, termId: int):
    pass

### patient medical history ###
def get_history(userId: int) -> dict:
    pass

def add_condition(userId: int, termId: int, conditionInfo: dict) -> dict:
    pass

def update_condition(userId: int, termId: int, conditionInfo: dict) -> dict:
    pass

def delete_condition(userId: int, termId: int, conditionInfo: dict) -> dict:
    pass

def add_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict) -> dict:
    pass

def update_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict) -> dict:
    pass

def delete_prescription(userId: int, conditionTermId: int, prescriptionTermId: int, prescritptionInfo: dict) -> dict:
    pass
