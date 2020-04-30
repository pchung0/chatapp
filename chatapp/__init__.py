from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cfe3c1b7cb40b32ec7df7161a139f9ba'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sql.db'
# app.config['SQLALCHEMY_ECHO'] = True

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


db = SQLAlchemy(app)
socketio = SocketIO(app)

from chatapp import routes