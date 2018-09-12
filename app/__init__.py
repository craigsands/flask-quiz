import os
from shutil import copyfile
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

bootstrap = Bootstrap()
#login = LoginManager()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        # DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
        # SQLALCHEMY_DATABASE_URI=os.environ.get(
        #     'DATABASE_URL',
        #     'sqlite:///' + os.path.join(app.instance_path, 'app.sqlite')
        # ),
        # SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        os.makedirs(os.path.join(app.instance_path, 'quiz'))
    except OSError:
        pass

    copyfile(
        'sample-quiz.xlsx',
        os.path.join(app.instance_path, 'quiz', 'sample-quiz.xlsx')
    )

    bootstrap.init_app(app)
    #login.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.quiz import bp as quiz_bp
    app.register_blueprint(quiz_bp, url_prefix='/quiz')

    return app


from app import models
