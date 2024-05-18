import hashlib
import uuid

from .glovars import PASSWORD_SALT
from . import terminal_style


def salted_hash(password: str):
    hashAlg = 'sha256'
    hash = hashlib.new(hashAlg)

    msg = PASSWORD_SALT + '|' + password
    hash.update(msg.encode())

    return hash.hexdigest()


def print_info(str: str):
    terminal_style.fontBrightWhite()
    print(f'[INFO] {str}')
    terminal_style.reset()


def gen_session_token() -> str:
    return uuid.uuid4().hex
