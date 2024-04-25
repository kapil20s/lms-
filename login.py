from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from model import db, User
from werkzeug.security import check_password_hash

# Create a Blueprint for authentication
auth = Blueprint('auth', __name__)

# Login route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Fetch user by username
        user = User.query.filter_by(username=username).first()

        # Check user and password
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')

# Registration route
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return redirect(url_for('auth.register'))

        # Create new user and hash password
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        # Add new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Login the user
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template('register.html')

# Logout route
@auth.route('/logout')
@login_required
def logout():
    # Logout user using Flask-Login
    logout_user()
    return redirect(url_for('index'))
