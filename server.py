from threading import Lock
from flask import Flask, render_template, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from draw.gamemaster import GameMaster

async_mode = None
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread_lock = Lock()

thread = None
gm = GameMaster()

t = 10

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def messaging(message):
    print(message)
    emit('server_response', {'data': message})

@socketio.on('buy_ticket')
def buy(message):
    buy_ticket_response = gm.buy_ticket()
    print(buy_ticket_response)
    emit('server_response', {'data': buy_ticket_response})



@socketio.on('connect')
def socket_connect():
    emit('server_response', {'data': 'Connected', 'count': 0})

@socketio.on('disconnect')
def socket_disconnect():
    print('Client disconnected')

# @socketio.event
# def disconnect_request():
#     @copy_current_request_context
#     def can_disconnect():
#         disconnect()
#
#     # for this emit we use a callback function
#     # when the callback function is invoked we know that the message has been
#     # received and it is safe to disconnect
#     emit('my_response',
#          {'data': 'Disconnected!'},
#          callback=can_disconnect)


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(countdown)
    emit('my_response', {'data': 'Connected'})


def countdown():
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


#TODO class refactor
#  thread class override threading
# try to handle not broadcase format
if __name__ == '__main__':
    socketio.run(app)
