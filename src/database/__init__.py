import os
from ..glovars import DB_PATH


def init_sqlite():
    # TODO
    return

def __init():
    if not os.path.isfile(DB_PATH):
        init_sqlite()

    return

__init()
