import functools
import datetime
from flask import request, session
from flask_login import current_user
from flask_socketio import join_room, leave_room, close_room, disconnect
from chatapp import socketio, db
from chatapp.models import Room, Message, User


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


# @socketio.on('my event')
# @authenticated_only
# def handle_my_custom_event(json, methods=['GET', 'POST']):
#     print('received msg: ' + str(json))


@socketio.on('connect')
@authenticated_only
def handle_connect():
    for room in current_user.rooms:
        join_room(room.id)
        print(f'room info: {room.id} {room.name}')
    # socketio.emit('room info', room)


@socketio.on('send')
@authenticated_only
def handle_send(msg):
    msg['datetime'] = datetime.datetime.now().strftime('%I:%M %p | %b %d')
    socketio.emit('message', msg, room=int(msg['room_id']))
    message = Message(message=msg['message'], room_id=msg['room_id'], user_id=msg['user_id'])
    db.session.add(message)
    db.session.commit()


# @socketio.on('create')
# @authenticated_only
# def handle_create(room_name):
#     room = Room(name=room_name, owner_id=current_user.id)
#     room.users.append(current_user)
#     db.session.add(room)
#     db.session.commit()

#     join_room(room.id)
#     socketio.emit('redirect room', room.id)
#     socketio.send(
#         f'{current_user.username} has entered the room.', room=room.id)


# @socketio.on('join')
# @authenticated_only
# def handle_join(room_name):
#     room = Room.query.filter_by(name=room_name).first()
#     if room:
#         room.users.append(current_user)
#         db.session.commit()
#         join_room(room.name)


# @socketio.on('delete')
# @authenticated_only
# def handle_invite(data):
#     room_id = data['room_id']
#     room = Room.query.filter_by(id=room_id).first()
#     if room and current_user.id == room.owner_id:
#         print('askldjfkljasdklfjaklsdfj')
#         close_room(room_id)
#         db.session.delete(room)
#         db.session.commit()

# @socketio.on('invite')
# @authenticated_only
# def handle_invite(data):
#     # room = User.query.join(User.rooms, aliased=True).filter_by(Room.id==data['room_id']).first()
#     # User.query.join(User.rooms, aliased=True).filter(Room.id==data['room_id']).first():
#     # room = Room.query.join(Room.users, aliased=True).filter(User.id==current_user.id).filter(Room.id==data['room_id']).first()
#     room = Room.query.filter_by(id=data['room_id']).first()
#     if not current_user in room.users: return
#     for username in data['users']:
#         user = User.query.filter_by(username=username).first()
#         if user:
#             room.users.append(user)
#     db.session.commit()


    # room = Room.query.filter_by(name=room_name).first()
    # if room:
    #     room.users.append(current_user)
    #     db.session.commit()
    #     join_room(room.name)


# @socketio.on('leave')
# @authenticated_only
# def handle_leave():
#     uid = current_user.get_id()
#     room = rooms[uid]
#     print(rooms)
#     rooms.pop(uid)
#     leave_room(room)
#     print(str(uid) + ' has left the room "' + str(room) + '".')
#     socketio.send(uid + ' has left the room.', room=room)