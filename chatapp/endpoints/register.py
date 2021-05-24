from chatapp import db
from chatapp.form import RegistrationForm
from chatapp.models import User
from flask import redirect, render_template, url_for
from flask.views import MethodView
from flask_login import current_user
from werkzeug.security import generate_password_hash


class Register(MethodView):
    def get(self):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        form = RegistrationForm()
        return render_template('register.html', form=form)

    def post(self):
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


def register(app):
    app.add_url_rule("/register", view_func=Register.as_view("register"))
