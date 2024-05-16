# src/database/message_op.py
from peewee import DoesNotExist
from datetime import datetime

from .data_models import MedicalTerm, MedicalTermInfo, Message, MessageTermCache, MedicalTermSynonym, MessageTranslationCache

def get_chat_messages(room_id: int, page_num: int, limit_num: int, language_code: str) -> dict:
    offset = (page_num - 1) * limit_num
    room_messages = Message.select().where(Message.room == room_id).order_by(Message.id).limit(limit_num).offset(offset)
    room_message_list = []

    for room_message in room_messages:
        room_message_list.append(get_message(room_id, room_message.id, language_code))

    return room_message_list

def get_message(room_id: int, message_id: int, language_code: str) -> dict:
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

    ret = {
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

    return ret


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

    # Create the main term entry
    new_term = MedicalTerm.create(term_type=term_type)
    new_term.save()

    # Create term info entries for each language
    for term_info in term_info_list:
        MedicalTermInfo.create(
            medical_term=new_term.id,
            language_code=term_info.get('languageCode', 'en'),
            name=term_info.get('name'),
            description=term_info.get('description'),
            url=term_info.get('url')
        )

        # Create synonyms for each language
        for synonym in term_info.get('synonyms', []):
            MedicalTermSynonym.create(
                medical_term=new_term.id,
                synonym=synonym.get('synonym'),
                language_code=synonym.get('languageCode', term_info.get('languageCode', 'en'))
            )

    return new_term.id

def get_term(term_id, language_code):
    medical_term = MedicalTerm.get(MedicalTerm.id == term_id)
    medical_term_info = MedicalTermInfo.get(
        (MedicalTermInfo.medical_term == term_id) & 
        (MedicalTermInfo.language_code == language_code)
    )

    ret = {
        "medicalTermId": term_id,
        "medicalTermType": medical_term.term_type,
        "name": medical_term_info.name,
        "description": medical_term_info.description,
        "medicalTermLinks": [
            medical_term_info.url
        ]
    }

    return ret

def get_terms_all(language_code: str):
    medical_terms = MedicalTerm.select()
    term_list = []

    for medical_term in medical_terms:
        term_id = medical_term.id
        term_info = get_term(term_id, language_code)
        term_list.append(term_info)

    ret = {
        "medicalTerms": term_list
    }

    return ret

def update_term(term_id: int, term_update_info: dict, language_code: str):
    """
    Update a medical term and its translation in a specified language.

    Parameters:
    - term_id: ID of the medical term to be updated
    - term_update_info: Dictionary containing updated term information and synonyms
      - Expected structure:
        {
            "termType": "CONDITION",  # Optional
            "name": "COVID-19",
            "description": "COVID-19 is a severe respiratory disease caused by a novel coronavirus.",
            "url": "https://www.nhs.uk/conditions/coronavirus-covid-19/",
            "synonyms": [
                {"synonym": "COVID"},
                {"synonym": "COVID-19"},
                {"synonym": "Corona"},
                {"synonym": "COVID 19"},
                {"synonym": "Scary COVID"}
            ]
        }
    - language_code: Language code for the translation

    Returns:
    - Updated term information
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
        # Delete existing synonyms for this term and language
        MedicalTermSynonym.delete().where(
            (MedicalTermSynonym.medical_term == term_id) &
            (MedicalTermSynonym.language_code == language_code)
        ).execute()

        # Add new synonyms
        for synonym in term_update_info.get('synonyms', []):
            MedicalTermSynonym.create(
                medical_term=term_id,
                synonym=synonym.get('synonym'),
                language_code=language_code
            )

    term.save()
    return get_term(term_id, language_code)

def delete_term(term_id: int):
    term = MedicalTerm.get(MedicalTerm.id == term_id)
    term.delete_instance()
    return

def create_link(message_id, term_id, original_synonym_id=None, translated_synonym_id=None):
    new_cache = MessageTermCache.create(
        medical_term=term_id,
        message=message_id,
        original_synonym=original_synonym_id,
        translated_synonym=translated_synonym_id
    )
    new_cache.save()

    return message_id, term_id

def delete_linking_term(message_id, term_id):
    try:
        term_link = MessageTermCache.get((MessageTermCache.message == message_id) & (MessageTermCache.medical_term == term_id))
        term_link.delete_instance()
        return True
    except DoesNotExist:
        return False

def get_message_terms(message_id, language_code):
    message_term_cache = MessageTermCache.select().where(MessageTermCache.message == message_id)
    terms_list = []

    for cache in message_term_cache:
        term_id_in_cache = cache.medical_term.id
        term = get_term(term_id_in_cache, language_code)
        terms_list.append(term)

    return terms_list

# TODO: THis is just a template. Please get the right information and put it in
def search_medical_terms(query):
    # Search for the term directly or by synonyms
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

# TODO: THis is just a template. Please get the right information and put it in
def save_message(roomId, userId, original_text, translated_text, medical_terms, translated_medical_terms):
    message = Message.create(
        User_id=userId,
        Room_id=roomId,
        Text=original_text,
        Send_time=datetime.now()
    )
    message.save()
    
    MessageTranslationCache.create(
        Message_id=message.id,
        Language_code=user_language,
        Translated_text=translated_text
    ).save()

    for term in medical_terms:
        MessageTermCache.create(
            Message_id=message.id,
            MedicalTerm_id=term['id'],
            Original_language_synonym=term['synonym'],
            Translated_language_synonym=None
        ).save()

    for term in translated_medical_terms:
        cache = MessageTermCache.get(
            MessageTermCache.Message_id == message.id,
            MessageTermCache.MedicalTerm_id == term['id']
        )
        cache.Translated_language_synonym = term['synonym']
        cache.save()

    return message
