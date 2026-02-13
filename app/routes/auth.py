from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User

auth = Blueprint('auth', __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        # Check if it's a student login (roll number) or admin (username)
        roll_number = request.form.get('roll_number')
        username = request.form.get('username')
        password = request.form.get('password')

        if username: # Admin login attempt
            user = User.query.filter_by(username=username, role='admin').first()
        else: # Student login attempt
            user = User.query.filter_by(roll_number=roll_number, role='student').first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
            else:
                return redirect(next_page) if next_page else redirect(url_for('student.dashboard'))
        else:
            flash('Login Unsuccessful. Please check credentials', 'danger')

    return render_template('auth/login.html', title='Login')

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
