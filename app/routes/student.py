from flask import render_template, Blueprint, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Exam, Question, Option, ExamAttempt, Response
from datetime import datetime
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

student = Blueprint('student', __name__)

@student.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    active_exams = Exam.query.filter_by(is_active=True).all()
    return render_template('student/dashboard.html', exams=active_exams)

@student.route("/exam/<int:exam_id>/instructions")
@login_required
def instructions(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    return render_template('student/instructions.html', exam=exam)

@student.route("/exam/<int:exam_id>/start", methods=['POST'])
@login_required
def start_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    # Check if attempt already exists
    attempt = ExamAttempt.query.filter_by(user_id=current_user.id, exam_id=exam_id, status='in_progress').first()
    if not attempt:
        attempt = ExamAttempt(
            user_id=current_user.id,
            exam_id=exam_id,
            time_left=exam.duration * 60,
            status='in_progress'
        )
        db.session.add(attempt)
        db.session.commit()

        # Initialize responses for all questions
        questions = Question.query.filter_by(exam_id=exam_id).all()
        for q in questions:
            resp = Response(attempt_id=attempt.id, question_id=q.id, status='not_visited')
            db.session.add(resp)
        db.session.commit()

    return redirect(url_for('student.exam_interface', attempt_id=attempt.id))

@student.route("/exam/interface/<int:attempt_id>")
@login_required
def exam_interface(attempt_id):
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != current_user.id or attempt.status == 'submitted':
        return redirect(url_for('student.dashboard'))

    exam = Exam.query.get(attempt.exam_id)
    questions = Question.query.filter_by(exam_id=exam.id).all()
    responses = {r.question_id: r for r in attempt.responses}

    return render_template('student/exam.html', exam=exam, attempt=attempt, questions=questions, responses=responses)

def decrypt_payload(encrypted_data):
    key = b'1234567812345678'
    iv = b'1234567812345678'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(base64.b64decode(encrypted_data)), AES.block_size)
    return json.loads(decrypted.decode('utf-8'))

@student.route("/exam/save_response", methods=['POST'])
@login_required
def save_response():
    if 'encrypted_data' in request.json:
         data = decrypt_payload(request.json['encrypted_data'])
    else:
         data = request.json

    attempt_id = data.get('attempt_id')
    question_id = data.get('question_id')
    status = data.get('status')

    response = Response.query.filter_by(attempt_id=attempt_id, question_id=question_id).first()
    if response:
        response.status = status
        response.answer_text = data.get('answer_text')
        response.selected_options = data.get('selected_options')
        response.time_spent += data.get('time_spent', 0)
        db.session.commit()

    # Update attempt time left
    attempt = ExamAttempt.query.get(attempt_id)
    attempt.time_left = data.get('time_left')
    db.session.commit()

    return jsonify({'status': 'success'})

@student.route("/exam/log_event", methods=['POST'])
@login_required
def log_event():
    if 'encrypted_data' in request.json:
         data = decrypt_payload(request.json['encrypted_data'])
    else:
         data = request.json
    attempt_id = data.get('attempt_id')
    event_type = data.get('event_type')

    attempt = ExamAttempt.query.get(attempt_id)
    if attempt and attempt.user_id == current_user.id:
        if event_type == 'tab_switch':
            attempt.tab_switches += 1
            db.session.commit()
            return jsonify({'status': 'success', 'switches': attempt.tab_switches})
    return jsonify({'status': 'error'}), 400

@student.route("/exam/submit", methods=['POST'])
@login_required
def submit_exam():
    if 'encrypted_data' in request.json:
         data = decrypt_payload(request.json['encrypted_data'])
    else:
         data = request.json
    attempt_id = data.get('attempt_id')
    attempt = ExamAttempt.query.get(attempt_id)
    if attempt and attempt.user_id == current_user.id:
        attempt.status = 'submitted'
        attempt.end_time = datetime.utcnow()
        db.session.commit()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400
