from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# RECAPTCHA_PUBLIC_KEY = '6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J'
# RECAPTCHA_PRIVATE_KEY = '6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cfe3c1b7cb40b32ec7df7161a139f9ba'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# db = SQLAlchemy(app)
socketio = SocketIO(app)

from chatapp import routes