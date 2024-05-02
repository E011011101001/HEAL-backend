import os
from ..glovars import DB_PATH


def init_sqlite():
    # TODO
    return

def __init():
    if DB_PATH:
        if not os.path.isfile(DB_PATH):
            init_sqlite()
    else:
        print("FATAL: DB_PATH is not set. Exiting...")
        exit()

    return

__init()
