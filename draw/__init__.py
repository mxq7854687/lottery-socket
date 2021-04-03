from flask import Flask
from flask_socketio import SocketIO

from . import gamemaster as g

async_mode = None
socketio = SocketIO(async_mode=async_mode)
gm = g.GameMaster()


def init_app(debug=True):
    app = Flask(__name__)
    app.debug = debug

    from .flask_app import app as app_scheme

    app.register_blueprint(app_scheme)

    socketio.init_app(app)
    return app
