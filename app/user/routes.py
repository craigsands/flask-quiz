from flask import current_app, render_template
from flask_login import login_required
from app.user import bp
from app.models import User


@bp.route('/')
@login_required
def index():
    users = User.query.all()
    return render_template('user/index.html', users=users)


@bp.route('/<username>')
@login_required
def get_stats(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/stats.html', title='User Statistics',
                           user=user)
