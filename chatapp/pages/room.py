from chatapp.models import Room
from flask import redirect, render_template, session, url_for
from flask.views import MethodView
from flask_login import current_user, login_required


class RoomPage(MethodView):
    decorators = [login_required]

    def get(self, room_id=None):
        if room_id is None:
            return render_template('room.html', current_room=None)

        session['room'] = room_id
        room = Room.query.filter_by(id=room_id).first()
        if room and current_user in room.users:
            return render_template('room.html', current_room=room)
        return redirect(url_for('home'))


def register(app):
    app.add_url_rule("/", view_func=RoomPage.as_view("home"))
    app.add_url_rule("/rooms/<int:room_id>",
                     view_func=RoomPage.as_view("room"))
