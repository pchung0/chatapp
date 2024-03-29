from chatapp import db
from chatapp import models as m
from flask import jsonify, request, session
from flask.json import jsonify
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_socketio import close_room, leave_room


class Room(MethodView):
    decorators = [login_required]

    def get(self, room_id):
        '''get room data: id, name, owner, messages, and users'''
        room = m.Room.query.filter_by(id=room_id).first()
        if room:
            messages = [{'message': msg.message, 'user_id': msg.user_id,
                        'datetime': msg.datetime.strftime('%I:%M %p | %b %d'),
                         'username': msg.user.username} for msg in room.messages]
            usernames = [user.username for user in room.users]
            data = {
                'id': room_id,
                'name': room.name,
                'owner': room.owner.username,
                'messages': messages,
                'users': usernames,
            }
            return jsonify(data)
        return '0'

    def delete(self, room_id):
        '''delete the room'''
        room = m.Room.query.filter_by(id=room_id).first()
        if room and current_user.id == room.owner_id:
            close_room(str(room.id), session['sid'])
            db.session.delete(room)
            m.Message.query.filter_by(room_id=room_id).delete()
            db.session.commit()
            return '1'
        elif current_user in room.users:
            leave_room(str(room.id), session['sid'], '/')
            room.users.remove(current_user)
            db.session.commit()
            return '1'
        return '0'


def register(app):
    app.add_url_rule("/api/rooms/<int:room_id>",
                     view_func=Room.as_view("room_api"))
