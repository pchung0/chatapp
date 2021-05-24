from flask import jsonify
from flask.views import MethodView
from flask_login import current_user, login_required


class Rooms(MethodView):
    decorators = [login_required]

    def get(self):
        rooms = [{'id': room.id, 'name': room.name, 'owner_id': room.owner_id}
                 for room in current_user.rooms]
        return jsonify(rooms)


def register(app):
    app.add_url_rule("/rooms", view_func=Rooms.as_view("rooms"))
