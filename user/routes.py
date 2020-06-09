from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_socketio import join_room, leave_room
from user import app, login_manager, db
from user.form import RegistrationForm, LoginForm
from user.models import User, Room


@app.route('/')
@login_required
def home():
    # rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
    # print(f'cu: {current_user.session_id}')
    # return render_template('index.html', rooms=[{'id':1, 'name':'room1'}])
    return redirect('http://127.0.0.1:5001/')


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
