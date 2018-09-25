from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.associationproxy import association_proxy
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode, index=True, unique=True)
    pw_hash = db.Column(db.Unicode)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # quizzes (parent, 1 -> many)
    # scores (parent, 1 -> many)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def get(self, user_id):
        print('gotten')
        return self.query.filter_by(id=user_id).first()


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_question'
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), primary_key=True)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'))
    prompt = db.Column(db.Unicode)
    correct_answer = db.Column(db.Unicode)

    def __repr__(self):
        return '<Question %r>' % self.id


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, index=True, unique=True)

    def __repr__(self):
        return '<Subject %r>' % self.name


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode, index=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Quiz %r>' % self.name


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Float)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Score %r, User %r, Quiz %r>' % (
            self.score, self.user.name, self.quiz.name)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
