# src/database/message_op.py
from peewee import DoesNotExist
from datetime import datetime

from .data_models import MedicalTerm, MedicalTermTranslation, Message, MessageTermCache, MedicalTermSynonym

def get_chat_messages(roomId: int, pageNum: int, limNum: int, language_code: str) -> dict:
    offset = (pageNum - 1) * limNum
    roomMessages = Message.select().where(Message.Room_id == roomId).order_by(Message.id).limit(limNum).offset(offset)
    roomMessageList = []

    for roomMessage in roomMessages:
        roomMessageList.append(get_message(roomId, roomMessage.id, language_code))

    return roomMessageList

def get_message(roomId: int, messageId: int, language_code: str) -> dict:
    message = Message.get((Message.Room_id == roomId) and (Message.id == messageId))

    medicalTermList = get_message_terms(messageId, language_code)

    # timestamp and content.metadata.translations are ignored
    ret = {
        "messageId": message.id,
        "roomId": message.Room_id.id,
        "senderUserId": message.User_id.id,
        "timestamp": message.Send_time,
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
    newTerm = MedicalTerm.create(
        Term_id=termInfo.get('name')
    )
    newTerm.save()

    newTranslation = MedicalTermTranslation.create(
        MedicalTerm_id=newTerm.id,
        Language_code="en",
        Description=termInfo.get('description'),
        URL=termInfo.get('medical_term_links')
    )
    newTranslation.save()

    return newTerm.id

def get_term(termId, language_code):
    medicalTerm = MedicalTerm.get(MedicalTerm.id == termId)
    translation = MedicalTermTranslation.get(
        (MedicalTermTranslation.MedicalTerm_id == termId) & 
        (MedicalTermTranslation.Language_code == language_code)
    )

    ret = {
        "medicalTermId": termId,
        "medicalTermType": medicalTerm.MedicalTerm_type,
        "name": translation.Name,
        "description": translation.Description,
        "medicalTermLinks": [
            translation.URL
        ]
    }

    return ret

def get_terms_all(language_code: str):
    medicalTermAll = MedicalTerm.select()
    termList = []

    for medicalTerm in medicalTermAll:
        termId = medicalTerm.id
        termInfo = get_term(termId, language_code)

        termList.append(termInfo)

    ret = {
        "medicalTerms": termList
    }

    return ret

def update_term(termId: int, termUpdateInfo: dict):
    term = MedicalTerm.get(MedicalTerm.id == termId)
    translation = MedicalTermTranslation.get(MedicalTermTranslation.MedicalTerm_id == termId)

    if 'term_id' in termUpdateInfo:
        term.Term_id = termUpdateInfo.get('term_id')

    if 'language_code' in termUpdateInfo:
        translation.Language_code = termUpdateInfo.get('language_code')

    if 'description' in termUpdateInfo:
        translation.Description = termUpdateInfo.get('description')

    if 'URL' in termUpdateInfo:
        translation.URL = termUpdateInfo.get('URL')

    term.save()
    translation.save()
    return term

def delete_term(termId: int):
    term = MedicalTerm.get(MedicalTerm.id == termId)
    term.delete_instance()
    return

def create_link(messageId, termId):
    newCache = MessageTermCache.create(
        MedicalTerm_id=termId,
        Message_id=messageId
    )

    newCache.save()

    message = Message.get(Message.id == messageId)
    termInfo = get_term(termId)
    termsInfoInCache = get_message_terms(messageId)

    ret = {
        "message": {
            "messageId": messageId,
            "senderUserId": message.User_id.id,
            "sendTime": message.Send_time,
            "message": message.Text,
            "medicalTerms": termsInfoInCache
        },
        "MedicalTerm": termInfo
    }

    return ret

def get_message_terms(messageId, language_code):
    messageTermCache = MessageTermCache.select().where(MessageTermCache.Message_id == messageId)
    termsList = []

    for cache in messageTermCache:
        termIdInCache = cache.MedicalTerm_id.id
        term = get_term(termIdInCache, language_code)
        termsList.append(term)

    ret = {
        "medicalTerms": termsList
    }

    return ret

def search_medical_terms(query):
    # Search for the term directly or by synonyms
    medical_terms = MedicalTerm.select().join(MedicalTermSynonym).where(
        (MedicalTerm.Term_id.contains(query)) |
        (MedicalTermSynonym.Synonym.contains(query))
    )

    results = []
    for term in medical_terms:
        term_translations = MedicalTermTranslation.select().where(MedicalTermTranslation.MedicalTerm_id == term.id)
        translations = [{
            "language": trans.Language_code,
            "default_name": trans.Name,
            "description": trans.Description,
            "url": trans.URL
        } for trans in term_translations]
        results.append({
            "term_id": term.id,
            "medical_term_type": term.MedicalTerm_type,
            "translations": translations
        })

    return results