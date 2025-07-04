from flask import Flask
import os
from dotenv import load_dotenv
from flask_login import LoginManager

# Load environment variables from .env file
load_dotenv()

from sage_chat.database import db # Import the db object
from sage_chat.cli_commands import create_db_command, load_sages_command # Import the CLI commands
from sage_chat.routes.index import index_bp
from sage_chat.routes.chat_routes import chat_bp
from sage_chat.routes.auth_routes import auth_bp
from sage_chat.model.user import User # Import the User model

# Get the absolute path of the directory containing app.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the static folder, assuming it's one level up
static_path = os.path.join(current_dir, '..', 'static')
# Construct the path to the template folder, assuming it's one level up
template_path = os.path.join(current_dir, '..', 'template')

app = Flask(__name__, static_folder=static_path, template_folder=template_path)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Disable tracking modifications

# Initialize SQLAlchemy with the app
db.init_app(app)

# Set a secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a_very_secret_key_for_dev') # Use a strong, random key in production!

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login' # Specify the login view for redirection

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(index_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(auth_bp)

# Register CLI commands
app.cli.add_command(create_db_command)
app.cli.add_command(load_sages_command)

if __name__ == '__main__':
    app.run(debug=True)
