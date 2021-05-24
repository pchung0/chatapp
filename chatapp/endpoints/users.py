from chatapp.models import Room, User
from flask import jsonify, request
from flask.views import MethodView


class Users(MethodView):
    def get(self):
        room = request.args.get('room', default=0, type=int)
        nonmembers = request.args.get('nonmembers', default=0, type=int)

        if not room and not nonmembers:
            return jsonify(self.get_all_users())
        elif room and not nonmembers:
            return jsonify(self.get_room_users(room))
        elif room and nonmembers:
            return jsonify(list(set(self.get_all_users()) - set(self.get_room_users(room))))
        return jsonify([])

    def get_all_users(self) -> list[str]:
        usernames = User.query.with_entities(User.username).all()
        usernames = [username[0] for username in usernames]
        return usernames

    def get_room_users(self, room_id: int) -> list[str]:
        if room := Room.query.filter_by(id=room_id).first():
            usernames = [
                user.username for user in room.users if user.id == room.owner_id]
            usernames.extend(
                [user.username for user in room.users if user.id != room.owner_id])
            return usernames
        return []


def register(app):
    app.add_url_rule("/users", view_func=Users.as_view("users"))
