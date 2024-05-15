from peewee import DoesNotExist
from datetime import datetime

from .data_models import MedicalTerm, Message, MessageTermCache

def get_chat_messages(roomId: int, pageNum: int, limNum: int) -> dict:

    offset = (pageNum - 1) * limNum
    roomMessages = Message.select().where(Message.Room_id == roomId).order_by(Message.id).limit(limNum).offset(offset)
    roomMessageList = []

    for roomMessage in roomMessages:
        roomMessageList.append(get_message(roomId, roomMessage.id))

    return roomMessageList

def get_message(roomId: int, messageId: int) -> dict:
    message = Message.get((Message.Room_id == roomId) and (Message.id == messageId))

    medicalTermList = get_message_terms(messageId)

    # timestamp and content.metadata.translations are ignored
    ret = {
        "messageId": message.id,
        "roomId": message.Room_id,
        "senderUserId": message.User_id,
        "timestamp": "",
        "content": {
            "text": message.Text,
            "metadata": {
                "translations": {},
                "medicalTerms": medicalTermList
            }
        }
    }

    return ret

def get_term(termId):
    pass

def get_message_terms(messageId):
    pass
