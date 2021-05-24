import functools
from flask import render_template, redirect, url_for, flash, session, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from flask_socketio import join_room, leave_room, disconnect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from chatapp import app, login_manager, db, socketio
from chatapp.form import RegistrationForm, LoginForm
from chatapp.models import User, Room
from chatapp.socket import *


@app.route('/')
@login_required
def home():
    rooms = [{'id': room.id, 'name': room.name} for room in current_user.rooms]
    return render_template('room.html', current_room=None)


@app.route('/room', methods=['POST'])
@login_required
def create_room():
    if request.get_json():
        room_name = request.json['room_name']
        print(room_name)
        room = Room(name=room_name, owner_id=current_user.id)
        room.users.append(current_user)
        db.session.add(room)
        db.session.commit()
        print(room.id)
        join_room(room.id, current_user.session_id, '/')
        socketio.send(
            f'{current_user.username} has entered the room.', room=room.id)
        return {'name': room_name, 'id': room.id}
    return '0'


@app.route('/room/<path:room_id>', methods=['GET'])
@login_required
def enter_room(room_id):
    if 'room' in session:
        leave_room(session['room'], current_user.session_id, '/')
    session['room'] = room_id
    room = Room.query.filter_by(id=room_id).first()
    if room and current_user in room.users:
        join_room(room_id, current_user.session_id, '/')
        rooms = [{'id': room.id, 'name': room.name}
                 for room in current_user.rooms]
        return render_template('room.html', current_room=room)
    return redirect(url_for('home'))


@app.route('/room/<path:room_id>', methods=['DELETE'])
@login_required
def delete_room(room_id):
    room = Room.query.filter_by(id=room_id).first()
    print('--------------------')
    print(room)
    if room and current_user.id == room.owner_id:
        close_room(room.id, current_user.session_id)
        db.session.delete(room)
        Message.query.filter_by(room_id=room_id).delete()
        db.session.commit()
        return '1'
    elif current_user in room.users:
        leave_room(room.id, current_user.session_id, '/')
        room.users.remove(current_user)
        db.session.commit()
        return '1'
    return '0'


@app.route('/room/<path:room_id>/data', methods=['GET'])
@login_required
def room_message(room_id):
    room = Room.query.filter_by(id=room_id).first()
    if room:
        messages = [{'message': msg.message, 'user_id': msg.user_id,
                     'datetime': msg.datetime.strftime('%I:%M %p | %b %d'),
                     'username': msg.user.username} for msg in room.messages]
        usernames = [
            user.username for user in room.users if user.id == room.owner_id]
        usernames.extend(
            [user.username for user in room.users if user.id != room.owner_id])
        data = {'id': room_id, 'name': room.name, 'owner_id': room.owner_id,
                'messages': messages, 'users': usernames}
        return data
    return '0'


@app.route('/room/<path:room_id>/users', methods=['Get'])
@login_required
def get_room_users(room_id):
    room = Room.query.filter_by(id=room_id).first()
    if current_user in room.users:
        usernames = [
            user.username for user in room.users if user.id == room.owner_id]
        usernames.extend(
            [user.username for user in room.users if user.id != room.owner_id])
        return jsonify(usernames)
    return '0'


@app.route('/room/<path:room_id>/users', methods=['POST'])
@login_required
def invite_users(room_id):
    if request.get_json():
        room = Room.query.filter_by(id=room_id).first()
        if current_user in room.users:
            for username in request.json['users']:
                user = User.query.filter_by(username=username).first()
                if user:
                    room.users.append(user)
            db.session.commit()
            return '1'
    return '0'


@app.route('/room_list', methods=['GET'])
@login_required
def room_list():
    rooms = [{'id': room.id, 'name': room.name, 'owner_id': room.owner_id}
             for room in current_user.rooms]
    return jsonify(rooms)


@app.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.with_entities(User.id, User.username).all()
    return jsonify(users)


@app.route('/room/<path:room_id>/not_members', methods=['GET'])
@login_required
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
        print(form.username.errors)
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # flash('Login Suceed')
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            flash('Login Failed. Please check username and password', 'danger')
    return render_template('login.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))