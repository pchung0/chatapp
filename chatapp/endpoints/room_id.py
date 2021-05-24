from chatapp import db
from chatapp.models import Message, Room
from flask import redirect, render_template, session, url_for
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_socketio import close_room, join_room, leave_room


class RoomId(MethodView):
    decorators = [login_required]

    def get(self, room_id):
        if 'room' in session:
            leave_room(session['room'], current_user.session_id, '/')
        session['room'] = room_id
        room = Room.query.filter_by(id=room_id).first()
        if room and current_user in room.users:
            join_room(room_id, current_user.session_id, '/')
            rooms = [{'id': room.id, 'name': room.name}
                     for room in current_user.rooms]
            return render_template('room.html', current_room=room)
        return redirect(url_for('home'))

    def delete(self, room_id):
        room = Room.query.filter_by(id=room_id).first()
        print('--------------------')
        print(room)
        if room and current_user.id == room.owner_id:
            close_room(room.id, current_user.session_id)
            db.session.delete(room)
            Message.query.filter_by(room_id=room_id).delete()
            db.session.commit()
            return '1'
        elif current_user in room.users:
            leave_room(room.id, current_user.session_id, '/')
            room.users.remove(current_user)
            db.session.commit()
            return '1'
        return '0'


def register(app):
    app.add_url_rule("/room/<path:room_id>",
                     view_func=RoomId.as_view("room_id"))
