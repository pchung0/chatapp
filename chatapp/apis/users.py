from chatapp.models import Room, User
from flask import jsonify, request
from flask.views import MethodView


class Users(MethodView):
    def get(self):
        room_id = request.args.get('room', default=0, type=int)
        nonmembers = request.args.get('nonmembers', default=0, type=int)

        if not room_id and not nonmembers:
            return jsonify(self.get_all_users())
        elif room_id and not nonmembers:
            return jsonify(self.get_room_users(room_id))
        elif room_id and nonmembers:
            return jsonify(list(set(self.get_all_users()) - set(self.get_room_users(room_id))))
        return jsonify([])

    @staticmethod
    def get_all_users() -> list[str]:
        usernames = User.query.with_entities(User.username).all()
        usernames = [username[0] for username in usernames]
        return usernames

    @staticmethod
    def get_room_users(room_id: int) -> list[str]:
        if room := Room.query.filter_by(id=room_id).first():
            usernames = [user.username for user in room.users]
            return usernames
        return []


def register(app):
    app.add_url_rule("/api/users", view_func=Users.as_view("users_api"))
