from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager
from chatapp import secretkey
import pkgutil
from importlib import import_module
from flask_session import Session

from .  import pages, apis

app = Flask(__name__)
app.config['SECRET_KEY'] = secretkey.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../sql.db'
app.config['SESSION_TYPE'] = 'filesystem'

# app.config['SQLALCHEMY_ECHO'] = True

login_manager = LoginManager(app)
# login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


Session(app)
db = SQLAlchemy(app)
socketio = SocketIO(app, manage_session=False)



def __register_endpoints(app):
    for _, endpoint_name, _ in pkgutil.iter_modules(pages.__path__):
        endpoint = import_module(f"{pages.__name__}.{endpoint_name}")
        register = getattr(endpoint, "register")
        register(app)
    for _, endpoint_name, _ in pkgutil.iter_modules(apis.__path__):
        endpoint = import_module(f"{apis.__name__}.{endpoint_name}")
        register = getattr(endpoint, "register")
        register(app)

from chatapp.socket import handle_connect, handle_send
__register_endpoints(app)
