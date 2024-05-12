import os

from ..glovars import DB_PATH
from ..utils import print_info
from . import data_models

from . import user_ops as user


def init_sqlite():
    data_models.init()
    return

def __init():
    if not os.path.isfile(DB_PATH):
        print_info(f'{DB_PATH} not found. Initializing...')
        init_sqlite()
    else:
        print_info(f'Found {DB_PATH}.')

    return

__init()
