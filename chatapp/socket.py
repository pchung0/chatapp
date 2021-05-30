import functools
import datetime
from flask import request, session
from flask_login import current_user
from flask_socketio import join_room, disconnect
from chatapp import socketio, db
from chatapp.models import Message


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('connect')
@authenticated_only
def handle_connect():
    session['sid'] = request.sid
    for room in current_user.rooms:
        join_room(str(room.id))


@socketio.on('send')
@authenticated_only
def handle_send(msg):
    msg['datetime'] = datetime.datetime.now().strftime('%I:%M %p | %b %d')
    socketio.emit('message', msg, to=str(msg['room_id']))
    message = Message(message=msg['message'],
                      room_id=msg['room_id'], user_id=msg['user_id'])
    db.session.add(message)
    db.session.commit()
