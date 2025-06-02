from flask import Blueprint, render_template, session, redirect, url_for
from guru_ai.database import db
from guru_ai.model.user import User

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = None
    if user_id:
        user = User.query.get(user_id)

    return render_template('index.html', user=user)
