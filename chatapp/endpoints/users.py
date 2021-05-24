from chatapp.models import User
from flask import jsonify
from flask.views import MethodView
from flask_login import login_required


class Users(MethodView):
    decorators = [login_required]

    def get(self):
        users = User.query.with_entities(User.id, User.username).all()
        return jsonify(users)


def register(app):
    app.add_url_rule("/users", view_func=Users.as_view("users"))
