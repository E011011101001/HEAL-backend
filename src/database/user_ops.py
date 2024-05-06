from peewee import DoesNotExist

from .data_models import User

def email_exists(email: str) -> bool:
    try:
        User.get(User.Email == email)
        return True
    except DoesNotExist:
        return False
