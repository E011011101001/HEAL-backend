from peewee import DoesNotExist

from .data_models import BaseUser

def email_exists(email: str) -> bool:
    try:
        BaseUser.get(BaseUser.Email == email)
        return True
    except DoesNotExist:
        return False
