import functools
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room, disconnect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from chatroom import app, login_manager, db, socketio
from chatroom.database import User, Room
from chatroom.socket import *

# import functools
# from flask_socketio import join_room, leave_room, disconnect
# from chatapp import socketio

@app.route('/')
@login_required
def home():
    rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
    return render_template('index2.html', rooms=rooms)
    # return render_template('session.html')

@app.route('/room/<path:new_room>')
@login_required
def enter_room(new_room):
    if 'room' in session:
        leave_room(session['room'], current_user.session_id, '/')
    session['room'] = new_room
    room = Room.query.filter_by(id=new_room).first()
    if room and current_user in room.users:
        join_room(new_room, current_user.session_id, '/')
        rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
        messages = [{'id':msg.id, 'message':msg.message} for msg in room.messages]
        print('////////////////////////')
        print(room.messages)
        print(room)
        return render_template('chatroom2.html', room_id=new_room, rooms=rooms, messages=messages)
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