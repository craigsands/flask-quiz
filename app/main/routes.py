from flask import redirect, url_for
from flask_login import current_user
from app.main import bp


# a simple page that says hello
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('user.get_info',
                                username=current_user.username))
    return redirect(url_for('auth.login'))
