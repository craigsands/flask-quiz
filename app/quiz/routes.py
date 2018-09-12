import os
import glob
from flask import current_app, redirect, render_template, request, session, url_for
from app.models import Quiz
from app.quiz import bp
from app.quiz.forms import AnswerForm


@bp.route('/')
def index():
    if not session.get('username'):
        return redirect(url_for('auth.login'))

    pattern = os.path.join(current_app.instance_path, 'quiz', '*.xlsx')

    items = [os.path.splitext(os.path.basename(f))[0] for f in glob.iglob(pattern)]

    return render_template('quiz/index.html', title='Quizzes', quizzes=items)


@bp.route('/<quiz_title>', methods=['GET', 'POST'])
def start(quiz_title):
    session['points'] = 0
    session['total_points'] = 0
    session['current_question_id'] = 0

    return redirect(url_for('quiz.get_question',
                            quiz_title=quiz_title,
                            question_id=0))


@bp.route('/<quiz_title>/<int:question_id>', methods=['GET', 'POST'])
def get_question(quiz_title, question_id):

    quiz = Quiz().load_from_excel(
        os.path.join(current_app.instance_path, 'quiz', '%s.xlsx' % quiz_title)
    )
    quiz.build_questions()

    num_questions = len(quiz.questions)

    question_id = int(question_id)

    if question_id >= num_questions:
        return redirect(url_for('quiz.get_question', quiz_title=quiz_title,
                                question_id=session.get(
                                    'current_question_id', 0
                                )))

    session['current_question_id'] = question_id

    question = quiz.questions[question_id]

    form = AnswerForm()

    if request.method == "POST":
        if form.validate_on_submit():
            session['total_points'] = session.get('total_points', 0) + 1

            answer = str(form.answer.data).strip()
            correct_answer = str(question['correct_answer']).strip()
            if answer == correct_answer:
                session['points'] = session.get('points', 0) + 1

            next_question = question_id + 1

            if next_question == num_questions:
                return redirect(url_for('quiz.get_results',
                                        quiz_title=quiz_title))

            return redirect(url_for('quiz.get_question',
                                    quiz_title=quiz_title,
                                    question_id=next_question))

        return redirect(url_for('quiz.get_question',
                                quiz_title=quiz_title,
                                question_id=question_id))
    else:
        section = question['section']
        known_key = list(question['known'].keys())[0]
        known_value = list(question['known'].values())[0]
        unknown_key = question['unknown']

        return render_template('quiz/question.html', title=quiz.title,
                               quiz_title=quiz_title,
                               question_num=question_id + 1,
                               num_questions=num_questions, section=section,
                               known_key=known_key, known_value=known_value,
                               unknown_key=unknown_key, form=form)


@bp.route('/<quiz_title>/results')
def get_results(quiz_title):
    points = session.pop('points', 0)
    total_points = session.pop('total_points', 0)
    return render_template('quiz/results.html', title=quiz_title,
                           quiz_title=quiz_title, points=points,
                           total_points=total_points)
