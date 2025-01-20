from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_socketio import SocketIO

from flask_migrate import Migrate

app = Flask(__name__)

# Create SocketIO for ChatRoom
socketio = SocketIO(app)
rooms = {
    "Main": {"members": 0, "messages": []} # This can be set to an empty dict and manipulated in routes instead to make it dynamic, but for now we just want one room
         }

# The secret key was generated using the 'secret' Python package. When pushed to production, generate new key and make env variable
app.config['SECRET_KEY'] = 'a037ea6e64f833615907ad19475804fb'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/../instance/site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app) # Used for hashing our passwords in the forms
login_manager = LoginManager(app)
login_manager.login_view = 'login' # Function name of the route (same as passed into url_for)
login_manager.login_message_category = 'info' # Bootstrap class

migrate = Migrate(app, db)

from cobochat import routes