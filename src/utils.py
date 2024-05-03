import hashlib

from .glovars import PASSWORD_SALT


def salted_hash(password):
    hashAlg = 'sha256'
    hash = hashlib.new(hashAlg)

    msg = PASSWORD_SALT + '|' + password
    hash.update(msg.encode())

    return hash.hexdigest()
