from werkzeug import exceptions
from peewee import DoesNotExist

from . import app


@app.errorhandler(exceptions.HTTPException)
def general_exceptions(e):
    return {
        "error": "internalServerError",
        "message": "The server encountered an unexpected condition that prevented it from fulfilling the request."
    }, 500


@app.errorhandler(DoesNotExist)
def does_not_exist_exception_handler(e):
    return {
        'error': 'instanceNotFoundError',
        'message': 'The specified item does not exist.'
    }, 404
