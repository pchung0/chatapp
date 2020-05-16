from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from user import secretkey

app = Flask(__name__)
app.config['SECRET_KEY'] = secretkey.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../sql.db'
# app.config['SQLALCHEMY_ECHO'] = True

login_manager = LoginManager(app)
# login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


db = SQLAlchemy(app)
socketio = SocketIO(app)

from user import routes