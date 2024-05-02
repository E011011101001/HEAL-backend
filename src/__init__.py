from flask import Flask
from flask_cors import CORS

import os

from . import glovars
from . import database


app = Flask(__name__)
CORS(app, supports_credentials=True)

from . import routes

if __name__ == '__main__':
    app.run()
