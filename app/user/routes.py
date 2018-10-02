from flask import request, render_template, url_for
from flask_login import login_required
from app.user import bp
from app.models import User


@bp.route('/')
@login_required
def index():
    return render_template('user/index.html', title='Users')


@bp.route('/<username>')
@login_required
def get_info(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/info.html', title='User Info', user=user)
