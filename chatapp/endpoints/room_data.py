from flask.json import jsonify
from chatapp.models import Room
from flask.views import MethodView
from flask_login import login_required


class RoomData(MethodView):
    decorators = [login_required]

    def get(self, room_id):
        room = Room.query.filter_by(id=room_id).first()
        if room:
            messages = [{'message': msg.message, 'user_id': msg.user_id,
                        'datetime': msg.datetime.strftime('%I:%M %p | %b %d'),
                         'username': msg.user.username} for msg in room.messages]
            usernames = [
                user.username for user in room.users if user.id == room.owner_id]
            usernames.extend(
                [user.username for user in room.users if user.id != room.owner_id])
            data = {'id': room_id, 'name': room.name, 'owner_id': room.owner_id,
                    'messages': messages, 'users': usernames}
            return jsonify(data)
        return '0'


def register(app):
    app.add_url_rule("/room/<path:room_id>/data",
                     view_func=RoomData.as_view("room_data"))
