from chatapp.form import LoginForm
from chatapp.models import User
from flask import flash, redirect, render_template, request, url_for
from flask.views import MethodView
from flask_login import current_user, login_user
from werkzeug.security import check_password_hash
from werkzeug.urls import url_parse


class LoginPage(MethodView):
    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        return render_template('login.html', form=form)

    def post(self):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = LoginForm()
        if form.validate_on_submit():
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


def register(app):
    app.add_url_rule("/login", view_func=LoginPage.as_view("login"))
