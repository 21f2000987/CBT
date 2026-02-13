from flask import render_template, url_for, flash, redirect, request, Blueprint, jsonify
from flask_login import current_user, login_required
from app import db, bcrypt
from app.models import User, Exam, Question, Option, SystemSetting
import json
import os
from werkzeug.utils import secure_filename
from flask import current_app

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def check_admin():
    if current_user.role != 'admin':
        flash('Access denied. Admin only.', 'danger')
        return redirect(url_for('student.dashboard'))

@admin.route("/dashboard")
def dashboard():
    exams = Exam.query.all()
    students = User.query.filter_by(role='student').all()
    return render_template('admin/dashboard.html', exams=exams, student_count=len(students), students=students)

@admin.route("/student/add", methods=['POST'])
def add_student():
    roll = request.form.get('roll_number')
    pwd = request.form.get('password')
    full_name = request.form.get('full_name')
    school_id = request.form.get('school_id')

    if User.query.filter_by(roll_number=roll).first():
        flash('Roll number already exists', 'danger')
    else:
        student = User(
            roll_number=roll,
            password=bcrypt.generate_password_hash(pwd).decode('utf-8'),
            role='student',
            full_name=full_name,
            school_id=school_id
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route("/exam/new", methods=['GET', 'POST'])
def new_exam():
    if request.method == 'POST':
        exam = Exam(
            title=request.form.get('title'),
            description=request.form.get('description'),
            duration=int(request.form.get('duration')),
            adaptive_mode='adaptive_mode' in request.form,
            is_full_screen_required='is_full_screen_required' in request.form
        )
        db.session.add(exam)
        db.session.commit()
        flash('Exam created successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/exam_form.html', title='New Exam')

@admin.route("/exam/<int:exam_id>/questions", methods=['GET', 'POST'])
def manage_questions(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    if request.method == 'POST':
        # Handled via AJAX usually, but for now simple form
        pass
    return render_template('admin/questions.html', exam=exam)

@admin.route("/exam/<int:exam_id>/question/add", methods=['POST'])
def add_question(exam_id):
    data = request.form
    q_type = data.get('question_type')

    image_path = None
    if 'question_image' in request.files:
        file = request.files['question_image']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # Add timestamp to avoid collisions
            from datetime import datetime
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            try:
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"
            except Exception as e:
                flash(f'Error saving image: {e}. Note: Vercel storage is read-only.', 'warning')

    question = Question(
        exam_id=exam_id,
        question_text=data.get('question_text'),
        question_type=q_type,
        difficulty=data.get('difficulty', 'medium'),
        marks=float(data.get('marks', 1.0)),
        negative_marks=float(data.get('negative_marks', 0.0)),
        image_path=image_path
    )
    db.session.add(question)
    db.session.flush() # Get question ID

    if q_type in ['MCQ', 'MSQ']:
        options = request.form.getlist('options')
        correct_indices = request.form.getlist('is_correct')
        for i, opt_text in enumerate(options):
            is_correct = str(i) in correct_indices
            option = Option(question_id=question.id, option_text=opt_text, is_correct=is_correct)
            db.session.add(option)

    db.session.commit()
    flash('Question added!', 'success')
    return redirect(url_for('admin.manage_questions', exam_id=exam_id))

@admin.route("/exam/<int:exam_id>/ai-generate", methods=['POST'])
def ai_generate_questions(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    topic = request.json.get('topic')
    count = int(request.json.get('count', 5))

    # In a real scenario, call Ollama/OpenAI here
    # Mocking AI response for demonstration
    mock_questions = []
    for i in range(count):
        mock_questions.append({
            'text': f'AI Generated Question {i+1} about {topic}',
            'type': 'MCQ',
            'difficulty': 'medium',
            'options': [
                {'text': 'Option A', 'correct': True},
                {'text': 'Option B', 'correct': False},
                {'text': 'Option C', 'correct': False},
                {'text': 'Option D', 'correct': False},
            ]
        })

    return jsonify(mock_questions)

@admin.route("/exam/<int:exam_id>/ai-approve", methods=['POST'])
def ai_approve_questions(exam_id):
    data = request.json
    questions_data = data.get('questions', [])

    for q_data in questions_data:
        question = Question(
            exam_id=exam_id,
            question_text=q_data.get('text'),
            question_type=q_data.get('type', 'MCQ'),
            difficulty=q_data.get('difficulty', 'medium'),
            marks=1.0
        )
        db.session.add(question)
        db.session.flush()

        if 'options' in q_data:
            for opt_data in q_data['options']:
                option = Option(
                    question_id=question.id,
                    option_text=opt_data.get('text'),
                    is_correct=opt_data.get('correct', False)
                )
                db.session.add(option)

    db.session.commit()
    return jsonify({'status': 'success'})

@admin.route("/exam/<int:exam_id>/results")
def view_results(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    attempts = ExamAttempt.query.filter_by(exam_id=exam_id).all()
    return render_template('admin/results.html', exam=exam, attempts=attempts)

@admin.route("/exam/<int:exam_id>/toggle", methods=['POST'])
def toggle_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    exam.is_active = not exam.is_active
    db.session.commit()
    return jsonify({'status': 'success', 'is_active': exam.is_active})
