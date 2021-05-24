from flask import redirect, url_for
from flask.views import MethodView
from flask_login import login_required, logout_user


class Logout(MethodView):
    decorators = [login_required]

    def get(self):
        logout_user()
        return redirect(url_for('login'))


def register(app):
    app.add_url_rule("/logout", view_func=Logout.as_view("logout"))
