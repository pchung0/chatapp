from chatapp import db
from chatapp.models import Room, User
from flask import jsonify, request
from flask.views import MethodView
from flask_login import current_user


class RoomUsers(MethodView):
    def get(self, room_id):
        '''get usernames of all users in the room'''
        if room := Room.query.filter_by(id=room_id).first():
            usernames = [user.username for user in room.users]
        else:
            usernames = []
        return jsonify(usernames)

    def post(self, room_id):
        '''add a new user to the room'''
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
    app.add_url_rule("/api/rooms/<int:room_id>/users",
                     view_func=RoomUsers.as_view("room_users_api"))
