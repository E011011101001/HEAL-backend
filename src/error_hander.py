from werkzeug import exceptions

from . import app


@app.errorhandler(exceptions.HTTPException)
def general_exceptions(e):
    return {
        "error": "internalServerError",
        "message": "The server encountered an unexpected condition that prevented it from fulfilling the request."
    }, 500
