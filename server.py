from threading import Lock

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from draw.gamemaster import GameMaster

async_mode = None
app = Flask(__name__)
socketio = SocketIO(app, async_mode=async_mode)
thread_lock = Lock()

thread = None
gm = GameMaster()

t = 10


@app.route('/')
def index() -> None:
    return render_template('index.html')


@socketio.on('message')
def messaging(message: str) -> None:
    emit('server_response', {'data': message})


@socketio.on('buy_ticket')
def buy(client_id: str) -> None:
    buy_ticket_response = gm.buy_ticket(client_id)
    emit('server_response', {'data': buy_ticket_response})


@socketio.on('connect')
def socket_connect() -> None:
    emit('server_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def socket_disconnect() -> None:
    print('Client disconnected')


@socketio.event
def connect() -> None:
    """
        thread for extra task countdown
    """
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(countdown)
    emit('my_response', {'data': 'Connected'})


def countdown() -> None:
    """
        broadcast timer through websocket
        broadcast result when timer end
    """
    time = t
    while True:
        while time > 0:
            socketio.emit('counter', {'data': time}, broadcast=True)
            socketio.sleep(1)
            time -= 1
        msg = gm.notify_winner()
        print(msg)
        socketio.emit('notification', {'data': msg}, broadcast=True)
        gm.restart()
        time = t


if __name__ == '__main__':
    socketio.run(app)
