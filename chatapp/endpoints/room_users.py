from chatapp import db
from chatapp.models import Room, User
from flask import jsonify, request
from flask.views import MethodView
from flask_login import current_user, login_required


class RoomUsers(MethodView):
    decorators = [login_required]

    def get(self, room_id):
        room = Room.query.filter_by(id=room_id).first()
        if current_user in room.users:
            usernames = [
                user.username for user in room.users if user.id == room.owner_id]
            usernames.extend(
                [user.username for user in room.users if user.id != room.owner_id])
            return jsonify(usernames)
        return '0'

    def post(self, room_id):
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


def register(app):
    app.add_url_rule("/room/<path:room_id>/users",
                     view_func=RoomUsers.as_view("room_users"))
