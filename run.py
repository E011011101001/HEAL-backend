from src import app as rawFlaskApp
from flask_socketio import SocketIO

appRunner = SocketIO(rawFlaskApp)

if __name__ == '__main__':
    appRunner.run(
        rawFlaskApp,
        host='0.0.0.0',
        port=8888,
        debug=True
    )
