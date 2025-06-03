from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from werkzeug.security import generate_password_hash, check_password_hash
from sage_chat.database import db
from sage_chat.model.user import User
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error_message = request.args.get('error') # Get error from query parameter
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user) # Log in the user with Flask-Login
            return redirect(url_for('index.index')) # Redirect to home page
        else:
            # For simplicity, just re-render with an error message.
            # In a real app, you'd pass this to the template.
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html', error=error_message) # Pass error to template

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    error_message = request.args.get('error') # Get error from query parameter
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('signup.html', error='Passwords do not match')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('signup.html', error='Email already registered')

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print(f"New user signed up: ID={new_user.id}, Email={new_user.email}")

        login_user(new_user) # Log in the new user with Flask-Login
        return redirect(url_for('index.index')) # Redirect to home page

    return render_template('signup.html', error=error_message) # Pass error to template

@auth_bp.route('/google-verify', methods=['POST'])
def google_verify():
    try:
        id_token_str = request.json.get('id_token')
        if not id_token_str:
            return jsonify({'success': False, 'message': 'No ID token provided'}), 400

        CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
        if not CLIENT_ID:
            return jsonify({'success': False, 'message': 'Google Client ID not configured on server'}), 500

        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), CLIENT_ID)

        userid = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')
        intent = request.json.get('intent') # Get the intent from the request

        user = User.query.filter_by(google_id=userid).first()
        if not user:
            # Check if user exists by email (if they previously signed up with email/password)
            existing_user_by_email = User.query.filter_by(email=email).first()
            if existing_user_by_email:
                # Link Google ID to existing account
                existing_user_by_email.google_id = userid
                existing_user_by_email.name = name # Update name from Google
                existing_user_by_email.profile_picture = picture # Store profile picture
                db.session.commit()
                user = existing_user_by_email # Set user to the existing user
            else:
                # If user doesn't exist by google_id or email
                if intent == 'signup':
                    # Create a new user if the intent is 'signup'
                    new_user = User(
                        email=email,
                        google_id=userid,
                        name=name,
                        profile_picture=picture
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    print(f"New Google user signed up: ID={new_user.id}, Email={new_user.email}")
                    user = new_user # Set user to the newly created user
                else:
                    # If intent is 'login' or not specified, return error
                    return jsonify({'success': False, 'message': 'User not found. Please sign up first.', 'redirect_url': url_for('auth.login', error='User not found. Please sign up first.')}), 200

        login_user(user) # Log in the user with Flask-Login
        print(f"Google User Authenticated: ID={user.id}, Email={user.email}, Name={user.name}, Profile Picture={user.profile_picture}")

        return jsonify({'success': True, 'message': 'Google login/signup successful', 'user': {'email': email, 'name': name}}), 200

    except ValueError as e:
        print(f"Invalid Google ID token: {e}")
        return jsonify({'success': False, 'message': 'Invalid Google ID token'}), 401
    except Exception as e:
        print(f"Server error during Google verification: {e}")
        return jsonify({'success': False, 'message': 'Server error during Google verification'}), 500

@auth_bp.route('/logout')
def logout():
    logout_user() # Log out the user with Flask-Login
    return redirect(url_for('auth.login')) # Redirect to login page after logout
