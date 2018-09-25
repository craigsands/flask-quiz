from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Score %r, User %r, Quiz %r>' % (
            self.score, self.user_id, self.quiz_id)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    #public = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    # bidirectional many-to-one reference for "User" object
    user = db.relationship('User', back_populates='quizzes')

    # proxy the 'name' attribute from the 'subject' relationship
    user_name = association_proxy('user', 'name')

    # association proxy of "quiz_question" collection
    # to "question" attribute
    questions = association_proxy('quiz_questions', 'question')

    def __repr__(self):
        return '<Quiz %r>' % self.name


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), primary_key=True)

    # bidirectional attribute/collection of "quiz"/"quiz_questions"
    user = db.relationship(
        Quiz,
        backref=db.backref("quiz_questions", cascade="all, delete-orphan")
    )

    # reference to the "Question" object
    question = db.relationship("Question")


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    prompt = db.Column(db.String(256))
    correct_answer = db.Column(db.String(64))

    # bidirectional many-to-one reference for "Subject" object
    subject = db.relationship('Subject', back_populates='questions')

    # proxy the 'name' attribute from the 'subject' relationship
    subject_name = association_proxy('subject', 'name')

    def __repr__(self):
        return '<Question %r>' % self.id


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    # bidirectional many-to-one reference for "Question" objects
    questions = db.relationship('Question', back_populates='subject')

    def __repr__(self):
        return '<Subject %r>' % self.name


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    pw_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='user', lazy='dynamic')

    # bidirectional many-to-one reference for "Quiz" objects
    quizzes = db.relationship('Quiz', back_populates='user')

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
