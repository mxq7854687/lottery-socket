from threading import Lock

from flask_socketio import emit

from .. import gm, socketio

thread_lock = Lock()

thread = None


@socketio.on("message")
def messaging(message: str) -> None:
    emit("server_response", {"data": message})


@socketio.on("buy_ticket")
def buy(client_id: str) -> None:
    buy_ticket_response = gm.buy_ticket(client_id)
    emit("server_response", {"data": buy_ticket_response})


@socketio.on("connect")
def socket_connect() -> None:
    emit("server_response", {"data": "Connected", "count": 0})


@socketio.on("disconnect")
def socket_disconnect() -> None:
    print("Client disconnected")


@socketio.event
def connect() -> None:
    """
    Thread for extra task countdown
    """
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(countdown)
    emit("my_response", {"data": "Connected"})


def countdown(t=10) -> None:
    """
    Broadcast timer through websocket
    Broadcast result when timer end
    """
    time = t
    while True:
        while time > 0:
            socketio.emit("counter", {"data": time}, broadcast=True)
            socketio.sleep(1)
            time -= 1
        msg = gm.notify_winner()
        print(msg)
        socketio.emit("notification", {"data": msg}, broadcast=True)
        gm.restart()
        time = t
