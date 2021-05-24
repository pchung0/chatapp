from chatapp.models import Room, User
from flask import jsonify
from flask.views import MethodView
from flask_login import current_user, login_required


class NotMembers(MethodView):
    decorators = [login_required]

    def get(self, room_id):
        room = Room.query.filter_by(id=room_id).first()
        room_users = {user.id for user in room.users}
        users = []
        if room and current_user in room.users:
            for user in User.query.with_entities(User.id, User.username).all():
                if user.id not in room_users:
                    users.append({'id': user.id, 'username': user.username})
            return jsonify(users)
        return '0'


def register(app):
    app.add_url_rule("/room/<path:room_id>/not_members",
                     view_func=NotMembers.as_view("not_members"))
