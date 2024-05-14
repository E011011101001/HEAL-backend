import os, sys
from dotenv import load_dotenv


# Fatal exit if None
def get_env_required(key: str):
    value = os.getenv(key)
    if value is None:
        sys.stderr.write(f"Fatal: {key} is not set. Exiting...")
        exit(1)

    return value


# .env
load_dotenv()

DB_PATH = get_env_required('DB_PATH')
PASSWORD_SALT = get_env_required('PASSWORD_SALT')


# # normal env
# DEBUG = bool(os.getenv('FLASK_DEBUG'))


# glovars
PATIENT = 1
DOCTOR = 2


# ENV
HOST='0.0.0.0'
PORT=8888
DEBUG=True
