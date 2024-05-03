from functools import wraps

from flask import request


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
                return ({
                    "error": "Missing items.",
                    "missing": missedItemList
                }, 406)
            else:
                return func(*args, **kwargs)

        return new_func

    return decorator
