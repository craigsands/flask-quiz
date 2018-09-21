import errno
import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import current_user, LoginManager
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_sqlalchemy import SQLAlchemy


bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
nav = Nav()


@nav.navigation()
def main_nav():
    n = Navbar(
        __name__,
        View('Home', 'main.index')
    )
    if current_user.is_authenticated:
        n.items.extend([
            View('Stats', 'user.get_stats', username=current_user.username),
            View('Quizzes', 'quiz.index'),
            View('Questions', 'question.index'),
            View('Logout', 'auth.logout')
        ])
    else:
        n.items.extend([
            View('Login', 'auth.login')
        ])
    return n


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # update config with environment variables or defaults
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', '^Ik7Jrzyi9#MA8ng'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URI',
            'sqlite:///' + os.path.join(app.instance_path, 'db.sqllite')
        ),
        SQLALCHEMY_ECHO=False,
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    # update config from instance/config.py if present
    app.config.from_pyfile('config.py', silent=True)

    # update from attributes of python object (usually TestCase)
    if test_config:
        app.config.from_object(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    # initialize extensions
    bootstrap.init_app(app)
    db.init_app(app)
    login.init_app(app)
    nav.init_app(app)

    # create the database
    db.create_all(app=app)

    # register module endpoints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.question import bp as question_bp
    app.register_blueprint(question_bp, url_prefix='/question')

    from app.quiz import bp as quiz_bp
    app.register_blueprint(quiz_bp, url_prefix='/quiz')

    from app.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    return app


from app import models
