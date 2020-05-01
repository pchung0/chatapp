import functools
from flask import request
from flask_login import current_user
from flask_socketio import join_room, leave_room, disconnect
from chatapp import socketio, db

rooms = {}

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketio.on('my event')
@authenticated_only
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received msg: ' + str(json))
    socketio.emit('my response', json)

@socketio.on('send')
@authenticated_only
def handle_send(json):
    print('received msg: ' + str(json))
    socketio.emit('message', json['message'], room=rooms[current_user.get_id()])

@socketio.on('create')
@authenticated_only
def handle_create(room):
    uid = current_user.get_id()
    join_room(room)
    rooms[uid] = room
    print(str(uid) + ' has entered the room "' + str(room) + '".')
    print(request.sid)
    socketio.send(str(uid) + ' has entered the room.', room=room)

@socketio.on('join')
@authenticated_only
def handle_join(room):
    uid = current_user.get_id()
    join_room(room)
    rooms[uid] = room
    print(str(uid) + ' has entered the room "' + str(room) + '".')
    print(request.sid)
    socketio.send(str(uid) + ' has entered the room.', room=room)

@socketio.on('leave')
@authenticated_only
def handle_leave():
    uid = current_user.get_id()
    room = rooms[uid]
    print(rooms)
    rooms.pop(uid)
    leave_room(room)
    print(str(uid) + ' has left the room "' + str(room) + '".')
    socketio.send(uid + ' has left the room.', room=room)