from peewee import DoesNotExist
from datetime import datetime

from .data_models import MedicalTerm, MedicalTermInfo, Message, MessageTermCache, MedicalTermSynonym, MessageTranslationCache

def get_chat_messages(room_id: int, page_num: int, limit_num: int, language_code: str) -> dict:
    """
    Get messages from a chat room.

    Parameters:
    room_id (int): ID of the room
    page_num (int): Page number for pagination
    limit_num (int): Number of messages per page
    language_code (str): Language code for translations

    Returns:
    dict: List of messages with translations and medical terms
    """
    offset = (page_num - 1) * limit_num
    room_messages = Message.select().where(Message.room == room_id).order_by(Message.id).limit(limit_num).offset(offset)
    room_message_list = []

    for room_message in room_messages:
        room_message_list.append(get_message(room_id, room_message.id, language_code))

    return room_message_list


def get_message(room_id: int, message_id: int, language_code: str) -> dict:
    """
    Get a message from a chat room.

    Parameters:
    room_id (int): ID of the room
    message_id (int): ID of the message
    language_code (str): Language code for translations

    Returns:
    dict: Message with translation and medical terms
    """
    message = Message.get((Message.room == room_id) & (Message.id == message_id))

    try:
        translation = MessageTranslationCache.get((MessageTranslationCache.message == message_id) & (MessageTranslationCache.language_code == language_code))
        translated_text = translation.translated_text
    except DoesNotExist:
        translated_text = message.text

    message_terms = MessageTermCache.select().where(MessageTermCache.message == message_id)
    medical_terms = [
        {
            'synonym': message_term.translated_synonym.synonym if message_term.translated_synonym else message_term.original_synonym.synonym,
            'termInfo': get_term(message_term.medical_term.id, language_code)
        } for message_term in message_terms
    ]

    return {
        "messageId": message.id,
        "roomId": message.room.id,
        "senderUserId": message.user.id,
        "timestamp": message.send_time,
        "content": {
            "text": message.text,
            "metadata": {
                "translation": translated_text,
                "medicalTerms": medical_terms
            }
        }
    }


def create_term(term_type, term_info_list):
    """
    Create a new medical term with translations and synonyms.

    Parameters:
    term_type (str): The type of the medical term (e.g., "CONDITION", "PRESCRIPTION", "GENERAL").
    term_info_list (list): A list of dictionaries, each containing the term information and synonyms for a specific language.
        Each dictionary should have the following keys:
        - language_code (str): The language code for the translation (default is 'en').
        - name (str): The name of the medical term in the specified language.
        - description (str): The description of the medical term in the specified language.
        - url (str): A URL with more information about the medical term (optional).
        - synonyms (list): A list of dictionaries, each containing a synonym and optionally a language_code.

    Example input:
    {
        "term_type": "CONDITION",
        "term_info_list": [
            {
                "language_code": "en",
                "name": "COVID-19",
                "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
                "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/",
                "synonyms": [
                    {"synonym": "COVID"},
                    {"synonym": "COVID-19"},
                    {"synonym": "Corona"},
                    {"synonym": "COVID 19"}
                ]
            },
            {
                "language_code": "jp",
                "name": "コロナウイルス",
                "description": "COVID-19は新型コロナウイルスによって引き起こされる重篤な呼吸器疾患です。",
                "url": "https://www3.nhk.or.jp/nhkworld/en/news/tags/82/",
                "synonyms": [
                    {"synonym": "コロナ"},
                    {"synonym": "新型コロナウイルス"}
                ]
            }
        ]
    }

    Returns:
    int: The ID of the newly created medical term.
    """
    if not term_info_list:
        raise ValueError("termInfoList cannot be empty")

    new_term = MedicalTerm.create(term_type=term_type)
    new_term.save()

    for term_info in term_info_list:
        MedicalTermInfo.create(
            medical_term=new_term.id,
            language_code=term_info.get('languageCode', 'en'),
            name=term_info.get('name'),
            description=term_info.get('description'),
            url=term_info.get('url')
        )

        for synonym in term_info.get('synonyms', []):
            MedicalTermSynonym.create(
                medical_term=new_term.id,
                synonym=synonym.get('synonym'),
                language_code=synonym.get('languageCode', term_info.get('languageCode', 'en'))
            )

    return new_term.id


def get_term(term_id, language_code):
    """
    Get information about a medical term.

    Parameters:
    term_id (int): ID of the medical term
    language_code (str): Language code for the response

    Returns:
    dict: Information about the medical term
    """
    medical_term = MedicalTerm.get(MedicalTerm.id == term_id)
    medical_term_info = MedicalTermInfo.get(
        (MedicalTermInfo.medical_term == term_id) & 
        (MedicalTermInfo.language_code == language_code)
    )

    return {
        "medicalTermId": term_id,
        "medicalTermType": medical_term.term_type,
        "name": medical_term_info.name,
        "description": medical_term_info.description,
        "medicalTermLinks": [
            medical_term_info.url
        ]
    }


def get_terms_all(language_code: str):
    """
    Get all medical terms.

    Parameters:
    language_code (str): Language code for the response

    Returns:
    dict: List of all medical terms
    """
    medical_terms = MedicalTerm.select()
    term_list = []

    for medical_term in medical_terms:
        term_id = medical_term.id
        term_info = get_term(term_id, language_code)
        term_list.append(term_info)

    return {
        "medicalTerms": term_list
    }


def update_term(term_id: int, term_update_info: dict, language_code: str):
    """
    Update a medical term and its translation in a specified language.

    Parameters:
    term_id (int): ID of the medical term to be updated
    term_update_info (dict): Updated information about the term and synonyms
    language_code (str): Language code for the translation

    Example input:
    {
        "termType": "CONDITION",
        "name": "COVID-19 Updated",
        "description": "Updated description.",
        "url": "https://updated-url.com",
        "synonyms": [
            {"synonym": "Updated COVID"},
            {"synonym": "Updated Corona"}
        ]
    }

    Returns:
    dict: Updated information about the medical term
    """
    term = MedicalTerm.get(MedicalTerm.id == term_id)

    if 'termType' in term_update_info:
        term.term_type = term_update_info.get('termType')

    translation, created = MedicalTermInfo.get_or_create(
        medical_term=term_id,
        language_code=language_code,
        defaults={
            'name': term_update_info.get('name'),
            'description': term_update_info.get('description'),
            'url': term_update_info.get('url')
        }
    )

    if not created:
        if 'name' in term_update_info:
            translation.name = term_update_info.get('name')

        if 'description' in term_update_info:
            translation.description = term_update_info.get('description')

        if 'url' in term_update_info:
            translation.url = term_update_info.get('url')

        translation.save()

    if 'synonyms' in term_update_info:
        MedicalTermSynonym.delete().where(
            (MedicalTermSynonym.medical_term == term_id) &
            (MedicalTermSynonym.language_code == language_code)
        ).execute()

        for synonym in term_update_info.get('synonyms', []):
            MedicalTermSynonym.create(
                medical_term=term_id,
                synonym=synonym.get('synonym'),
                language_code=language_code
            )

    term.save()
    return get_term(term_id, language_code)


def delete_term(term_id: int):
    """
    Delete a medical term.

    Parameters:
    term_id (int): ID of the medical term
    """
    term = MedicalTerm.get(MedicalTerm.id == term_id)
    term.delete_instance()


def create_link(message_id, term_id, original_synonym_id=None, translated_synonym_id=None):
    """
    Create a link between a message and a medical term.

    Parameters:
    message_id (int): ID of the message
    term_id (int): ID of the medical term
    original_synonym_id (int): ID of the original synonym (optional)
    translated_synonym_id (int): ID of the translated synonym (optional)

    Returns:
    tuple: IDs of the message and the term
    """
    new_cache = MessageTermCache.create(
        medical_term=term_id,
        message=message_id,
        original_synonym=original_synonym_id,
        translated_synonym=translated_synonym_id
    )
    new_cache.save()
    return message_id, term_id


def delete_linking_term(message_id, term_id):
    """
    Delete a link between a message and a medical term.

    Parameters:
    message_id (int): ID of the message
    term_id (int): ID of the medical term

    Returns:
    bool: True if the link was deleted, False otherwise
    """
    try:
        term_link = MessageTermCache.get((MessageTermCache.message == message_id) & (MessageTermCache.medical_term == term_id))
        term_link.delete_instance()
        return True
    except DoesNotExist:
        return False


def get_message_terms(message_id, language_code):
    """
    Get all medical terms linked to a message.

    Parameters:
    message_id (int): ID of the message
    language_code (str): Language code for the response

    Returns:
    list: List of medical terms linked to the message
    """
    message_term_cache = MessageTermCache.select().where(MessageTermCache.message == message_id)
    terms_list = []

    for cache in message_term_cache:
        term_id_in_cache = cache.medical_term.id
        term = get_term(term_id_in_cache, language_code)
        terms_list.append(term)

    return terms_list


def search_medical_terms(query):
    """
    Search for medical terms by name or synonym.

    Parameters:
    query (str): Search query

    Returns:
    list: List of medical terms matching the query
    """
    medical_terms = MedicalTerm.select().join(MedicalTermSynonym).where(
        (MedicalTerm.term_type.contains(query)) |
        (MedicalTermSynonym.synonym.contains(query))
    )

    results = []
    for term in medical_terms:
        term_translations = MedicalTermInfo.select().where(MedicalTermInfo.medical_term == term.id)
        translations = [{
            "language": trans.language_code,
            "default_name": trans.name,
            "description": trans.description,
            "url": trans.url
        } for trans in term_translations]

        synonyms = MedicalTermSynonym.select().where(MedicalTermSynonym.medical_term == term.id)
        synonym_list = [{
            "synonym": synonym.synonym,
            "language": synonym.language_code
        } for synonym in synonyms]

        results.append({
            "term_id": term.id,
            "medical_term_type": term.term_type,
            "translations": translations,
            "synonyms": synonym_list
        })

    return results


def save_message(room_id, user_id, original_text, translated_text, medical_terms, translated_medical_terms):
    """
    Save a new message and its translations and medical terms.

    Parameters:
    room_id (int): ID of the room
    user_id (int): ID of the user
    original_text (str): Original message text
    translated_text (str): Translated message text
    medical_terms (list): List of original medical terms
    translated_medical_terms (list): List of translated medical terms

    Returns:
    Message: The newly created message
    """
    message = Message.create(
        user=user_id,
        room=room_id,
        text=original_text,
        send_time=datetime.now()
    )
    message.save()

    MessageTranslationCache.create(
        message=message.id,
        language_code=user.language_code,
        translated_text=translated_text
    ).save()

    for term in medical_terms:
        MessageTermCache.create(
            message=message.id,
            medical_term=term['id'],
            original_synonym=term['synonym'],
            translated_synonym=None
        ).save()

    for term in translated_medical_terms:
        cache = MessageTermCache.get(
            MessageTermCache.message == message.id,
            MessageTermCache.medical_term == term['id']
        )
        cache.translated_synonym = term['synonym']
        cache.save()

    return message