import errno
import os
from datetime import datetime
from flask import (
    current_app, flash, redirect, render_template, request, session, url_for
)
from flask_login import current_user, login_required
from openpyxl import load_workbook
from werkzeug.utils import secure_filename
from app import db
from app.models import Question, Quiz, QuizQuestion, Subject
from app.quiz import bp
from app.quiz.forms import AnswerForm, UpdateQuizForm
from app.tables import SortableQuestionTable, SortableQuizTable


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    items_per_page = 10
    sort = request.args.get('sort', 'id')
    order = request.args.get('direction', 'asc')
    reverse = (order == 'desc')
    page = request.args.get('page', 1, type=int)
    quizzes = Quiz.query.order_by(
        getattr(getattr(Quiz, sort), order)()
    ).paginate(page, items_per_page, False)
    first_url = url_for('quiz.index', page=1) \
        if quizzes.has_prev else None
    prev_url = url_for('quiz.index', page=quizzes.prev_num) \
        if quizzes.has_prev else None
    next_url = url_for('quiz.index', page=quizzes.next_num) \
        if quizzes.has_next else None
    last_url = url_for('quiz.index', page=quizzes.pages) \
        if quizzes.has_next else None
    return render_template('quiz/index.html', title='Quizzes',
                           table=SortableQuizTable(
                               quizzes.items, sort_by=sort,
                               sort_reverse=reverse),
                           first_url=first_url, prev_url=prev_url,
                           next_url=next_url, last_url=last_url)


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    subjects = Subject.query.all()

    form = UpdateQuizForm()
    form.subjects.choices = [(s.id, s.name) for s in subjects]
    form.questions.choices = []

    if form.validate_on_submit():
        if request.method == "POST":
            quiz = Quiz()
            quiz.name = form.name.data
            quiz.user_id = current_user.get_id()
            quiz.subjects = form.subjects.data
            quiz.timestamp = datetime.utcnow()
            db.session.add(quiz)
            db.session.commit()
            return redirect(url_for('quiz.edit', quiz_id=quiz.id), 201)

    return render_template('quiz/create.html', title='Create Quiz', form=form)


@bp.route('/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def edit(quiz_id):
    quiz = Quiz.query.filter_by(id=quiz_id).first()
    subjects = Subject.query.all()

    form = UpdateQuizForm()
    form.name = quiz.name
    # TODO: HOW DO I GET quiz.subjects HERE???
    form.subjects.data = [s.id for s in quiz.subjects]
    form.subjects.choices = [(s.id, s.name) for s in subjects]

    if form.validate_on_submit():
        if request.method == "POST":
            items_per_page = 10
            sort = request.args.get('sort', 'id')
            order = request.args.get('direction', 'asc')
            reverse = (order == 'desc')
            page = request.args.get('page', 1, type=int)
            subject_ids = form.subjects.data
            questions = Question.query.filter(
                Question.subject_id.in_(subject_ids)).order_by(
                getattr(getattr(Question, sort), order)()
            ).paginate(page, items_per_page, False)
            first_url = url_for('question.index', page=1) \
                if questions.has_prev else None
            prev_url = url_for('question.index', page=questions.prev_num) \
                if questions.has_prev else None
            next_url = url_for('question.index', page=questions.next_num) \
                if questions.has_next else None
            last_url = url_for('question.index', page=questions.pages) \
                if questions.has_next else None
            return render_template('quiz/create.html', title=quiz.name,
                                   table=SortableQuestionTable(
                                       questions.items, sort_by=sort,
                                       sort_reverse=reverse),
                                   first_url=first_url, prev_url=prev_url,
                                   next_url=next_url, last_url=last_url)

    return render_template('quiz/edit.html', title='Edit Quiz', form=form,
                           quiz_name=quiz.name)


# @bp.route('/<quiz_name>', methods=['GET', 'POST'])
# @login_required
# def start(quiz_name):
#     session['points'] = 0
#     session['total_points'] = 0
#     session['current_question_id'] = 0
#
#     return redirect(url_for('quiz.get_question',
#                             quiz_name=quiz_name,
#                             question_id=0))
#
#
# @bp.route('/<quiz_title>/<int:question_id>', methods=['GET', 'POST'])
# @login_required
# def get_question(quiz_title, question_id):
#     pass
#     # quiz = Quiz().load_from_excel(
#     #     os.path.join(current_app.instance_path, 'quiz', '%s.xlsx' % quiz_title)
#     # )
#     # quiz.build_questions()
#     #
#     # num_questions = len(quiz.questions)
#     #
#     # question_id = int(question_id)
#     #
#     # if question_id >= num_questions:
#     #     return redirect(url_for('quiz.get_question', quiz_title=quiz_title,
#     #                             question_id=session.get(
#     #                                 'current_question_id', 0
#     #                             )))
#     #
#     # session['current_question_id'] = question_id
#     #
#     # question = quiz.questions[question_id]
#     #
#     # form = AnswerForm()
#     #
#     # if request.method == "POST":
#     #     if form.validate_on_submit():
#     #         session['total_points'] = session.get('total_points', 0) + 1
#     #
#     #         answer = str(form.answer.data).strip()
#     #         correct_answer = str(question['correct_answer']).strip()
#     #         if answer == correct_answer:
#     #             session['points'] = session.get('points', 0) + 1
#     #
#     #         next_question = question_id + 1
#     #
#     #         if next_question == num_questions:
#     #             return redirect(url_for('quiz.get_results',
#     #                                     quiz_title=quiz_title))
#     #
#     #         return redirect(url_for('quiz.get_question',
#     #                                 quiz_title=quiz_title,
#     #                                 question_id=next_question))
#     #
#     #     return redirect(url_for('quiz.get_question',
#     #                             quiz_title=quiz_title,
#     #                             question_id=question_id))
#     # else:
#     #     section = question['section']
#     #     known_key = list(question['known'].keys())[0]
#     #     known_value = list(question['known'].values())[0]
#     #     unknown_key = question['unknown']
#     #
#     #     return render_template('quiz/question.html', title=quiz.title,
#     #                            quiz_title=quiz_title,
#     #                            question_num=question_id + 1,
#     #                            num_questions=num_questions, section=section,
#     #                            known_key=known_key, known_value=known_value,
#     #                            unknown_key=unknown_key, form=form)
#
#
# @bp.route('/<quiz_title>/results')
# @login_required
# def get_results(quiz_title):
#     points = session.pop('points', 0)
#     total_points = session.pop('total_points', 0)
#     return render_template('quiz/results.html', title=quiz_title,
#                            quiz_title=quiz_title, points=points,
#                            total_points=total_points)
