# src/route_decorators.py

from functools import wraps
from flask import request
from datetime import datetime
from . import database as db

def required_body_items(item_list: list[str]):
    """
    Decorator to ensure that required items are present in the request body.

    Parameters:
    item_list (list[str]): List of required item keys.

    Returns:
    func: Wrapped function that checks for missing items before execution.

    Example:
    @required_body_items(['email', 'password'])
    def some_function():
        pass
    """
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            missed_item_list = []
            data = request.get_json()
            for item in item_list:
                if data.get(item) is None:
                    missed_item_list.append(item)

            if missed_item_list:
                return {
                    "error": "Missing items.",
                    "missing": missed_item_list
                }, 406
            else:
                return func(*args, **kwargs)
        return new_func
    return decorator

def required_params(item_list: list[str]):
    """
    Decorator to ensure that required parameters are present in the request URL.

    Parameters:
    item_list (list[str]): List of required parameter keys.

    Returns:
    func: Wrapped function that checks for missing parameters before execution.

    Example:
    @required_params(['page', 'limit'])
    def some_function():
        pass
    """
    def decorator(func):
        @wraps(func)
        def new_func(*args, **kwargs):
            missed_item_list = []
            for item in item_list:
                if request.args.get(item) is None:
                    missed_item_list.append(item)

            if missed_item_list:
                return {
                    "error": "Missing items.",
                    "missing": missed_item_list
                }, 406
            else:
                return func(*args, **kwargs)
        return new_func
    return decorator

def login_required(func):
    """
    Decorator to ensure that the user is authenticated and authorized.

    Parameters:
    func (func): Function to be wrapped.

    Returns:
    func: Wrapped function that checks for valid authorization before execution.

    Example:
    @login_required
    def some_function(user_id, language_code):
        pass
    """
    @wraps(func)
    def new_func(*args, **kwargs):
        unauth_error = {
            "error": "unauthorizedError",
        }
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
        except Exception:
            unauth_error['message'] = 'No Authorization Token'
            return unauth_error, 401

        user = db.user.get_user_by_token(token)
        if user is None or user['expirationTime'] < datetime.now():
            unauth_error['message'] = 'User invalid'
            return unauth_error, 401

        user_data = db.user.get_user_full(user['id'])
        language_code = user_data.get('language', 'en')

        return func(user['id'], language_code, *args, **kwargs)
    return new_func
