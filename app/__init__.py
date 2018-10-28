import errno
import logging
import os
from flask import Flask
from flask_babel import Babel, lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_login import current_user, LoginManager
from flask_mail import Mail
from flask_nav import Nav
from flask_nav.elements import Navbar, Subgroup, View
from flask_sqlalchemy import SQLAlchemy
from flask_restless import APIManager, ProcessingException
from logging.handlers import SMTPHandler


babel = Babel()
bootstrap = Bootstrap()
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()
manager = APIManager(flask_sqlalchemy_db=db)
nav = Nav()


@nav.navigation()
def main_nav():
    n = Navbar(__name__)
    if current_user.is_authenticated:
        n.items.extend([
            View('Home', 'user.get_info', username=current_user.username),
            View('Scores', 'user.get_scores'),
            Subgroup(
                'Quizzes',
                View('Manage', 'quiz.index'),
                #View('Create Quiz', 'quiz.create')
            ),
            Subgroup(
                'Questions',
                View('Manage', 'question.index'),
                View('Upload', 'question.upload')
            ),
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
        MAIL_SERVER=os.environ.get('MAIL_SERVER'),
        MAIL_PORT=int(os.environ.get('MAIL_PORT') or 25),
        MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS') is not None,
        MAIL_USERNAME=os.environ.get('MAIL_USERNAME'),
        MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD'),
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24)),
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
    babel.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    manager.init_app(app)
    nav.init_app(app)

    # create the database
    db.create_all(app=app)

    # register module endpoints
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

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

    # Create authentication wrapper for API requests
    def auth_func(*args, **kwargs):
        if not current_user.is_authenticated():
            raise ProcessingException(description='Not authenticated!',
                                      code=401)
        return True

    # register api endpoints
    from app.models import Quiz, Question, Score, Subject, User

    # Require app_context() or specify primary key for each table.
    # Otherwise, create_api() checks the database for the primary key before
    # the app context.
    with app.app_context():
        manager.create_api(Quiz, app=app,
                           methods=['GET', 'PATCH', 'POST', 'DELETE'],
                           allow_delete_many=True, results_per_page=0)
        manager.create_api(Question, app=app,
                           methods=['GET', 'POST', 'DELETE'],
                           allow_delete_many=True, results_per_page=0)
        manager.create_api(Score, app=app,
                           methods=['GET', 'POST', 'DELETE'],
                           allow_delete_many=True, results_per_page=0)
        manager.create_api(Subject, app=app,
                           methods=['GET', 'POST', 'DELETE'],
                           allow_delete_many=True, results_per_page=0)

        # TODO: Only modify self, unless admin
        # https://flask-restless.readthedocs.io/en/stable/customizing.html#universal-preprocessors-and-postprocessors
        manager.create_api(User, app=app, methods=['GET', 'POST'],
                           preprocessors=dict(POST=[auth_func],
                                              GET_MANY=[auth_func],
                                              PATCH_SINGLE=[auth_func],
                                              PATCH_MANY=[auth_func],
                                              PUT_SINGLE=[auth_func],
                                              PUT_MANY=[auth_func],
                                              DELETE_SINGLE=[auth_func],
                                              DELETE_MANY=[auth_func]),
                           primary_key='username')

        if not app.debug and not app.testing:
            if app.config['MAIL_SERVER']:
                auth = None
                if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                    auth = (app.config['MAIL_USERNAME'],
                            app.config['MAIL_PASSWORD'])
                secure = None
                if app.config['MAIL_USE_TLS']:
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                    fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                    toaddrs=app.config['ADMINS'], subject='Quick Quizzes Failure',
                    credentials=auth, secure=secure)
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)

    return app


from app import models
