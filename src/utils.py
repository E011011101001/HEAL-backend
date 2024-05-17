import hashlib
import uuid

from .glovars import PASSWORD_SALT


def salted_hash(password: str):
    hashAlg = 'sha256'
    hash = hashlib.new(hashAlg)

    msg = PASSWORD_SALT + '|' + password
    hash.update(msg.encode())

    return hash.hexdigest()


def print_info(str: str):
    print(f'[INFO] {str}')


def gen_session_token() -> str:
    return uuid.uuid4().hex