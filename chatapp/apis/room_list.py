from chatapp import db
from chatapp.models import Room
from flask import jsonify, request, session
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_socketio import join_room


class RoomList(MethodView):
    decorators = [login_required]

    def get(self):
        '''get a list of all joined rooms'''
        rooms = [{'id': room.id, 'name': room.name, 'owner': room.owner.username}
                 for room in current_user.rooms]
        return jsonify(rooms)

    def post(self):
        '''create a new room'''
        if request.get_json():
            room_name = request.json['room_name']
            room = Room(name=room_name, owner_id=current_user.id)
            room.users.append(current_user)
            db.session.add(room)
            db.session.commit()
            join_room(str(room.id), session['sid'], '/')
            return jsonify({'name': room_name, 'id': room.id})
        return '0'


def register(app):
    app.add_url_rule("/api/rooms", view_func=RoomList.as_view("room_list_api"))
