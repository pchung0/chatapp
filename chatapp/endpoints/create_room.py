from chatapp import db, socketio
from chatapp.models import Room
from flask import request, jsonify
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_socketio import join_room


class CreateRoom(MethodView):
    decorators = [login_required]

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
    app.add_url_rule(
        "/create_room", view_func=CreateRoom.as_view("create_room"))
