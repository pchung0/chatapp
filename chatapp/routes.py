from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_socketio import join_room, leave_room
from chatapp import app, login_manager, db, socket
from chatapp.form import RegistrationForm, LoginForm
from chatapp.database import User, Room
# from chatapp.socket import *

# import functools
# from flask_socketio import join_room, leave_room, disconnect
# from chatapp import socketio


@app.route('/')
@login_required
def home():
    rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
    # print(f'cu: {current_user.session_id}')
    return render_template('index.html', rooms=rooms)

@app.route('/room/<path:new_room>')
@login_required
def enter_room(new_room):
    print('++++++++++++++++')
    # print(session['_id'])
    # print(session['io'] )
    print(current_user.session_id)
    if 'room' in session:
        leave_room(session['room'], current_user.session_id, '/')
    session['room'] = new_room
    room = Room.query.filter_by(id=new_room).first()
    if room and current_user in room.users:
        join_room(new_room, current_user.session_id, '/')
        rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
        return render_template('chatroom.html', room_id=new_room, rooms=rooms)
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hased_password = generate_password_hash(form.password.data)
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    username=form.username.data,
                    password=hased_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        print('fail')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login Suceed')
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            flash('Login Failed')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))







# rooms = {}
# def authenticated_only(f):
#     @functools.wraps(f)
#     def wrapped(*args, **kwargs):
#         if not current_user.is_authenticated:
#             disconnect()
#         else:
#             return f(*args, **kwargs)
#     return wrapped

# @socketio.on('my event')
# @authenticated_only
# def handle_my_custom_event(json, methods=['GET', 'POST']):
#     print('received msg: ' + str(json))
#     socketio.emit('my response', json)

# @socketio.on('connect')
# @authenticated_only
# def handle_connect():
#     current_user.session_id = request.sid
#     print(current_user.session_id)
#     for room in current_user.rooms:
#         join_room(room.id)
#         print(f'room info: {room.id} {room.name}')
#     socketio.emit('room info', rooms)

# @socketio.on('send')
# @authenticated_only
# def handle_send(json):
#     print(type(request))
#     print('received msg: ' + str(json))
#     socketio.emit('message', json['message'], room=int(json['room_id']))

# @socketio.on('create')
# @authenticated_only
# def handle_create(room_name):
#     room = Room(name=room_name, owner_id=current_user.id)
#     room.users.append(current_user)
#     db.session.add(room)
#     db.session.commit()

#     join_room(room.id)
#     socketio.send(f'{current_user.username} has entered the room.', room=room.id)

# @socketio.on('join')
# @authenticated_only
# def handle_join(room_name):
#     room = Room.query.filter_by(name=room_name).first()
#     if room:
#         room.users.append(current_user)
#         db.session.commit()
#         join_room(room.name)

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