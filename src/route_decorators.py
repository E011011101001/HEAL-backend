# src/route_decorators.py
from functools import wraps

from flask import request

from datetime import datetime

from . import database as db


# Return a decorator that makes sure no item is missing before invoking func
# Generate 406 if missing anything
def required_body_items(itemList: list[str]):
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            missedItemList = []
            data = request.get_json()
            for item in itemList:
                if data.get(item) is None:
                    missedItemList.append(item)

            if missedItemList:
                return {
                    "error": "Missing items.",
                    "missing": missedItemList
                }, 406
            else:
                return func(*args, **kwargs)

        return new_func

    return decorator


def required_params(itemList: list[str]):
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            missedItemList = []
            for item in itemList:
                if request.args.get(item) is None:
                    missedItemList.append(item)

            if missedItemList:
                return {
                    "error": "Missing items.",
                    "missing": missedItemList
                }, 406
            else:
                return func(*args, **kwargs)

        return new_func

    return decorator

def login_required(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        unauthError = {
            "error": "unathorizedError",
        }
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
        except TypeError:
            unauthError['message'] = 'No Authorization Token'
            return unauthError, 401

        user = db.user.get_user_by_token(token)
        if user is None or user['expirationTime'] < datetime.now():
            unauthError['message'] = 'User invalid'
            return unauthError, 401

        user_data = db.user.get_user_full(user['id'])
        language_code = user_data.get('language', 'en')
        
        return func(user['id'], language_code, *args, **kwargs)

    return new_func