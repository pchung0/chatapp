import functools
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import join_room, leave_room, disconnect
from chatapp import app, socketio, login_manager, db
from chatapp.form import RegistrationForm, LoginForm
from chatapp.database import User


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            next = request.args.get('next')
            flash('Login Suceed')
            return redirect(next or url_for('home'))
        else:
            flash('Login Failed')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

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
def on_leave():
    uid = current_user.get_id()
    room = rooms[uid]
    print(rooms)
    rooms.pop(uid)
    leave_room(room)
    print(str(uid) + ' has left the room "' + str(room) + '".')
    socketio.send(uid + ' has left the room.', room=room)