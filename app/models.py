from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Unicode)
    correct_answer = db.Column(db.Unicode)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))

    # Questions (children) are many to one subject (parent)
    subject = db.relationship("Subject", back_populates="questions")

    # Quizzes (parents) are many to one question (child)
    quizzes = db.relationship("QuizQuestion", back_populates="question")

    def __repr__(self):
        return '<Question %r>' % self.id


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # User (parent) is one to many quizzes (children)
    user = db.relationship("User", back_populates="quizzes")

    # Scores (children) are many to one quiz (parent)
    scores = db.relationship("Score", back_populates="quiz")

    # Questions (children) are many to one quiz (parent)
    questions = db.relationship("QuizQuestion", back_populates="quiz")

    def __repr__(self):
        return '<Quiz %r>' % self.name


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'),
                            primary_key=True)

    # Quiz (parent) is one to many questions (children)
    quiz = db.relationship("Quiz", back_populates="questions")

    # Question (child) is one to many quizzes (parents)
    question = db.relationship("Question", back_populates="quizzes")


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # User (parent) is one to many scores (children)
    user = db.relationship("User", back_populates="scores")

    # Quiz (parent) is one to many scores (children)
    quiz = db.relationship("Quiz", back_populates="scores")

    def __repr__(self):
        return '<Score %r, User %r, Quiz %r>' % (
            self.score, self.user.name, self.quiz.name)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, index=True, unique=True)

    # Questions (children) are many to one subject (parent)
    questions = db.relationship("Question", back_populates="subject")

    def __repr__(self):
        return '<Subject %r>' % self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode, index=True, unique=True)
    pw_hash = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Quizzes (children) are many to one user (parent)
    quizzes = db.relationship("Quiz", back_populates="user")

    # Scores (children) are many to one user (parent)
    scores = db.relationship("Score", back_populates="user")

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
