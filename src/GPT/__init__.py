# src/GPT/__init__.py

from .chatbot import get_ai_doctor, ChatBot
from .translator import translate_to
from .chat_manager import translate, extract_medical_term, explain_medical_term, questioner_chat
from .highlighter import highlighter

__all__ = [
    'get_ai_doctor',
    'ChatBot',
    'translate_to',
    'translate',
    'extract_medical_term',
    'explain_medical_term',
    'questioner_chat',
    'highlighter'
]