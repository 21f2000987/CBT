import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()

def create_app():
    # Handle paths for PyInstaller bundle
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'app', 'templates')
        static_folder = os.path.join(sys._MEIPASS, 'app', 'static')
        app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    else:
        app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')

    # Use SQLite locally and PostgreSQL on Vercel/Production if DATABASE_URL is provided
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or f"sqlite:///{os.path.join(app.instance_path, 'site.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, 'uploads')

    # Ensure instance folder exists for SQLite
    if not os.path.exists(app.instance_path):
        try:
            os.makedirs(app.instance_path)
        except Exception as e:
            print(f"Warning: Could not create instance folder: {e}")

    # On Vercel, the filesystem is read-only. We try to create the folder but don't crash if it fails.
    try:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
    except Exception as e:
        print(f"Warning: Could not create upload folder: {e}")

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.routes.auth import auth
    from app.routes.admin import admin
    from app.routes.student import student

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(student)

    # Automatically create database tables for simplicity
    with app.app_context():
        db.create_all()

    return app
