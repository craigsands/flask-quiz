from flask import redirect, url_for
from app.main import bp


# a simple page that says hello
@bp.route('/')
@bp.route('/index')
def index():
    return redirect(url_for('quiz.index'))
