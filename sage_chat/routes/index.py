from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import current_user, login_required
from sage_chat.database import db
from sage_chat.model.user import User

index_bp = Blueprint('index', __name__)

@index_bp.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)
