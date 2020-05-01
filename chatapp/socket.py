import functools
from flask import request
from flask_login import current_user
from flask_socketio import join_room, leave_room, disconnect
from chatapp import socketio, db
from chatapp.database import Room

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

@socketio.on('connect')
@authenticated_only
def handle_connect():
    for room in current_user.rooms:
        join_room(room.id)
        print(f'room info: {room.id} {room.name}')
    socketio.emit('room info', rooms)

@socketio.on('send')
@authenticated_only
def handle_send(json):
    print('received msg: ' + str(json))
    socketio.emit('message', json['message'], room=rooms[current_user.get_id()])

@socketio.on('create')
@authenticated_only
def handle_create(room_name):
    room = Room(name=room_name, owner_id=current_user.id)
    room.users.append(current_user)
    db.session.add(room)
    db.session.commit()

    join_room(room.id)
    socketio.send(f'{current_user.username} has entered the room.', room=room)

@socketio.on('join')
@authenticated_only
def handle_join(room_name):
    room = Room.query.filter_by(name=room_name).first()
    if room:
        room.users.append(current_user)
        db.session.commit()
        join_room(room.name)

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