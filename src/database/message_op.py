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

def create_term(termInfo):

    # Language_code is default
    newTerm = MedicalTerm.create(
        Term_id = termInfo.get('name'),
        Language_code = "en",
        Discription = termInfo.get('description'),
        URL = termInfo.get('medical_term_links')
    )

    newTerm.save()

    return newTerm.id


def get_term(termId):
    pass

def get_terms_all():
    pass

def create_link(messageId, termId):
    newCache = MessageTermCache.create(
        MedicalTerm_id = termId,
        Message_id = messageId
    )

    newCache.save()

    # do I need room id?
    # where was sendTime?
    message = Message.get(Message.id == messageId)
    termInfo = get_term(termId)
    termsInfoInCache = get_message_terms(messageId)

    ret = {
        "message" : {
            "messageId" : messageId,
            "senderUserId": message.get('User_id'),
            "sendTime": "",
            "message": message.get('Text'),
            "medicalTerms": termsInfoInCache
        },
        "MedicalTerm" : termInfo
    }

    return ret

def get_message_terms(messageId):

    messageTermCache = MessageTermCache.select().where(MessageTermCache.Message_id == messageId)
    termsList = []

    for cache in messageTermCache:
        termIdInCache = cache.get('MedicalTerm_id')

        term = get_term(termIdInCache)
        termsList.append(term)

    ret = {
        "medicalTerms": termsList
    }

    return ret
