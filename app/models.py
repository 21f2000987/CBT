from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='student') # 'admin' or 'student'

    # Student specific
    roll_number = db.Column(db.String(20), unique=True, nullable=True)
    school_id = db.Column(db.String(20), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)

    attempts = db.relationship('ExamAttempt', backref='student', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.role}', '{self.roll_number}')"

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False) # In minutes
    is_active = db.Column(db.Boolean, default=False)
    is_full_screen_required = db.Column(db.Boolean, default=True)
    results_released = db.Column(db.Boolean, default=False)
    adaptive_mode = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    questions = db.relationship('Question', backref='exam', lazy=True, cascade="all, delete-orphan")
    attempts = db.relationship('ExamAttempt', backref='exam', lazy=True)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False) # MCQ, MSQ, SA, LA, NAT, Labeling, Code
    difficulty = db.Column(db.String(10), default='medium') # easy, medium, hard
    marks = db.Column(db.Float, default=1.0)
    negative_marks = db.Column(db.Float, default=0.0)
    image_path = db.Column(db.String(255)) # For questions with images/diagrams
    metadata_json = db.Column(db.JSON) # For labeling hotspots, code templates, etc.

    options = db.relationship('Option', backref='question', lazy=True, cascade="all, delete-orphan")

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    option_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

class ExamAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_progress') # in_progress, submitted
    time_left = db.Column(db.Integer) # seconds
    last_question_id = db.Column(db.Integer)
    tab_switches = db.Column(db.Integer, default=0)

    responses = db.relationship('Response', backref='attempt', lazy=True)

class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('exam_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.Text) # For SA, LA, NAT, Code
    selected_options = db.Column(db.String(200)) # Comma separated option IDs for MCQ/MSQ
    status = db.Column(db.String(20), default='not_visited') # answered, not_answered, marked, not_visited
    time_spent = db.Column(db.Integer, default=0) # seconds

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
