import functools
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, disconnect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from chatroom import app, login_manager, db, socketio
from chatroom.models import User, Room
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
