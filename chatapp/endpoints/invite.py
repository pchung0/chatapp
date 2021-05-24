from chatapp import db
from chatapp.models import Room, User
from flask import jsonify, request
from flask.views import MethodView
from flask_login import current_user, login_required


class Invite(MethodView):
    decorators = [login_required]

    def post(self):
        if request.get_json() and request.json['room_id']:
            room = Room.query.filter_by(id=request.json['room_id']).first()
            if current_user in room.users:
                for username in request.json['users']:
                    user = User.query.filter_by(username=username).first()
                    if user:
                        room.users.append(user)
                db.session.commit()
                return '1'
        return '0'


def register(app):
    app.add_url_rule("/invite", view_func=Invite.as_view("invite"))
