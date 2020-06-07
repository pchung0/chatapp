import functools
from flask import render_template, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, disconnect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from chatroom import app, login_manager, db, socketio
from chatroom.models import User, Room, Message
from chatroom.socket import *


@app.route('/')
@login_required
def home():
    # rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
    # return render_template('index2.html', rooms=rooms)
    # return render_template('session.html')
    rooms = [{'id': room.id, 'name': room.name} for room in current_user.rooms]
    return render_template('room.html', current_room=None, rooms=rooms, messages=[])


@app.route('/room/<path:new_room>', methods=['GET', 'POST'])
@login_required
def enter_room(new_room):
    if 'room' in session:
        leave_room(session['room'], current_user.session_id, '/')
    session['room'] = new_room
    room = Room.query.filter_by(id=new_room).first()
    if room and current_user in room.users:
        join_room(new_room, current_user.session_id, '/')
        rooms = [{'id': room.id, 'name': room.name} for room in current_user.rooms]
        # all_users = [{'id': id, 'username': username} for id, username in User.query.with_entities(User.id, User.username).all()]
        room_users = {user.id for user in room.users}
        users = []
        for user in User.query.with_entities(User.id, User.username).all():
            if user.id in room_users:
                users.append({'id': user.id, 'username': user.username, 'is_room_member':True})
            else:
                users.append({'id': user.id, 'username': user.username, 'is_room_member':False})

        # messages = [{'id': msg.id, 'message': msg.message, 'user_id': msg.user_id, 'datetime': msg.datetime} for msg in room.messages]
        return render_template('room.html', users=users, current_room=room, rooms=rooms, messages=room.messages)
        # return render_template('chatroom2.html', room_id=int(new_room), rooms=rooms, messages=messages)
    return redirect(url_for('home'))


# @app.route('/create_room', methods=['POST'])
# def create_room():
#     if request.get_json():
#         room_name = request.json['room_name']
#         room = Room(name=room_name, owner_id=current_user.id)
#         room.users.append(current_user)
#         db.session.add(room)
#         db.session.commit()

#         join_room(room.id)
#         socketio.emit('redirect room', room.id)
#         socketio.send(f'{current_user.username} has entered the room.', room=room.id)
#     return '1'

@app.route('/room/<path:room_id>/messages', methods=['GET'])
def room_message(room_id):
    print(int(room_id))
    print('************************')
    room = Room.query.filter_by(id=room_id).first()
    if room:
        messages = [{'message':msg.message, 'user_id':msg.user_id, 'datetime':msg.datetime.strftime('%I:%M %p | %b %d')} for msg in room.messages]
        return jsonify(messages)
    return '0'

@app.route('/room_list', methods=['GET'])
def room_list():
    rooms = [{'id': room.id, 'name': room.name} for room in current_user.rooms]
    return jsonify(rooms)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.with_entities(User.id, User.username).all()
    print('+++++++++++++++++++++++++')
    print(users)
    return jsonify(users)

@app.route('/room/<path:room_id>/not_members', methods=['GET'])
def get_not_member_users(room_id):

    room = Room.query.filter_by(id=room_id).first()
    room_users = {user.id for user in room.users}
    users = []
    if room and current_user in room.users:
        for user in User.query.with_entities(User.id, User.username).all():
            if user.id not in room_users:
                users.append({'id': user.id, 'username': user.username})
        return jsonify(users)

@app.route('/register', methods=['GET', 'POST'])
def register():
    return redirect('http://127.0.0.1:5000/register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    return redirect('http://127.0.0.1:5000/login')


@app.route("/logout")
@login_required
def logout():
    return redirect('http://127.0.0.1:5000/logout')
