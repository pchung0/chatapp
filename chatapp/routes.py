from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from chatapp import app, login_manager, db, socket
from chatapp.form import RegistrationForm, LoginForm
from chatapp.database import User


@app.route('/')
def home():
    rooms = [{'id':room.id, 'name':room.name} for room in current_user.rooms]
    return render_template('index.html', rooms=rooms)


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