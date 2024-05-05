import hashlib

from .glovars import PASSWORD_SALT


def salted_hash(password: str):
    hashAlg = 'sha256'
    hash = hashlib.new(hashAlg)

    msg = PASSWORD_SALT + '|' + password
    hash.update(msg.encode())

    return hash.hexdigest()


def print_info(str: str):
    print(f'[INFO] {str}')
