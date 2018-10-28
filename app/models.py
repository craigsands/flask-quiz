import base64
import jwt
import os
import uuid
from datetime import datetime, timedelta
from flask import current_app, url_for
from flask_login import current_user, UserMixin
from sqlalchemy import func, select
from sqlalchemy.orm import column_property
from sqlalchemy.ext.associationproxy import association_proxy
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


quiz_question_association_table = db.Table(
    'association', db.Model.metadata,
    db.Column('quiz_id', db.Integer, db.ForeignKey('quiz.id')),
    db.Column('question_id', db.Integer, db.ForeignKey('question.id'))
)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, index=True, unique=True,
                     default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                        default=lambda: current_user.id)
    locked = db.Column(db.Boolean, default=False)
    time_to_finish = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # User (parent) is one to many quizzes (children)
    user = db.relationship("User", back_populates="quizzes")

    # Proxy the 'username' attribute from the 'user' relationship
    user_name = association_proxy('user', 'username')

    # Scores (children) are many to one quiz (parent)
    scores = db.relationship("Score", back_populates="quiz", lazy='dynamic')

    # Questions (children) are many to many quizzes (parents)
    questions = db.relationship("Question",
                                secondary=quiz_question_association_table,
                                back_populates="quizzes", lazy='dynamic')

    def __repr__(self):
        return '<Quiz %r>' % self.name


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode)
    correct_answer = db.Column(db.Unicode)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    # Questions (children) are many to one subject (parent)
    subject = db.relationship("Subject", back_populates="questions")

    # Proxy the 'name' attribute from the 'subject' relationship
    subject_name = association_proxy('subject', 'name')

    # Quizzes (parents) are many to many questions (children)
    quizzes = db.relationship("Quiz",
                              secondary=quiz_question_association_table,
                              back_populates="questions", lazy='dynamic')

    def __repr__(self):
        return '<Question %r>' % self.id


Quiz.num_questions = column_property(
    select([func.count(quiz_question_association_table.c.question_id)]).
            where(quiz_question_association_table.c.quiz_id == Quiz.id).
            correlate_except(quiz_question_association_table)
)


Question.num_quizzes = column_property(
    select([func.count(quiz_question_association_table.c.quiz_id)]).
            where(quiz_question_association_table.c.question_id == Question.id).
            correlate_except(quiz_question_association_table)
)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    result = db.Column(db.UnicodeText)
    time_spent = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # User (parent) is one to many scores (children)
    user = db.relationship("User", back_populates="scores")

    # Proxy the 'username' attribute from the 'user' relationship
    user_name = association_proxy('user', 'username')

    # Quiz (parent) is one to many scores (children)
    quiz = db.relationship("Quiz", back_populates="scores")

    # Proxy the 'name' attribute from the 'quiz' relationship
    quiz_name = association_proxy('quiz', 'name')

    def __repr__(self):
        return '<Score %r, User %r, Quiz %r>' % (
            self.score, self.user.name, self.quiz.name)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, index=True, unique=True)

    # Questions (children) are many to one subject (parent)
    questions = db.relationship("Question", back_populates="subject",
                                lazy='dynamic')

    def __repr__(self):
        return '<Subject %r>' % self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode, index=True, unique=True)
    email = db.Column(db.Unicode, index=True, unique=True)
    password_hash = db.Column(db.Unicode)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # Quizzes (children) are many to one user (parent)
    quizzes = db.relationship("Quiz", back_populates="user", lazy='dynamic')

    # Scores (children) are many to one user (parent)
    scores = db.relationship("Score", back_populates="user", lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
