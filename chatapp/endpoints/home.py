from flask import render_template
from flask.views import MethodView
from flask_login import current_user, login_required


class Home(MethodView):
    decorators = [login_required]

    def get(self):
        rooms = [{'id': room.id, 'name': room.name}
                 for room in current_user.rooms]
        return render_template('room.html', current_room=None)


def register(app):
    app.add_url_rule("/", view_func=Home.as_view("home"))
