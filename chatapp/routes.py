from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
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
        print('suceed')
        return redirect(url_for('home'))
    else:
        print('fail')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        hased_password = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(form.password.data, user.password):
            login_user(user)
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        else:
            flash('Login Failed')
    return render_template('login.html', form=form)


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received msg: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)
