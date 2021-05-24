from chatapp import login_manager, db
from flask_login import UserMixin
import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

roomref = db.Table('roomref',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(26), nullable=False, default='Mike')
    last_name = db.Column(db.String(26), nullable=False, default='Stone')
    password = db.Column(db.String(120), nullable=False, default=123456)
    rooms = db.relationship('Room', secondary=roomref, back_populates='users')
    messages = db.relationship('Message', back_populates='user')

    session_id = -1

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('username is already taken')

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.first_name}', '{self.last_name}')"

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    users = db.relationship('User', secondary=roomref, back_populates='rooms')
    messages = db.relationship('Message', back_populates='room', passive_deletes=True)

    def __repr__(self):
        return f"Room('{self.id}', '{self.name}', '{self.owner_id}', '{self.users})"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    room = db.relationship('Room', back_populates='messages')
    user = db.relationship('User', back_populates='messages')

    def __repr__(self):
        return f"Message({self.room_id}, {self.user_id}, '{self.message}', {self.datetime})"
