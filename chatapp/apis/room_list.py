from chatapp import db
from chatapp.models import Room
from flask import jsonify, request
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_socketio import join_room


class RoomList(MethodView):
    decorators = [login_required]

    def get(self):
        rooms = [{'id': room.id, 'name': room.name, 'owner_id': room.owner_id}
                 for room in current_user.rooms]
        return jsonify(rooms)

    def post(self):
        if request.get_json():
            room_name = request.json['room_name']
            print(room_name)
            room = Room(name=room_name, owner_id=current_user.id)
            room.users.append(current_user)
            db.session.add(room)
            db.session.commit()
            print(room.id)
            join_room(room.id, current_user.session_id, '/')
            # socketio.send(
            #     f'{current_user.username} has entered the room.', room=room.id)
            return jsonify({'name': room_name, 'id': room.id})
        return '0'


def register(app):
    app.add_url_rule("/api/rooms", view_func=RoomList.as_view("room_list_api"))
