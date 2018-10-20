from flask import request, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.user import bp
from app.models import User


@bp.route('/')
@login_required
def index():
    # if not admin, return current user stats
    return redirect(url_for('user.get_info', username=current_user.username))
    # else
    #return render_template('user/info.html', title='User Info',
    #                       user_id=current_user.id)


@bp.route('/<username>')
@login_required
def get_info(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/info.html', title='User Info', user=user)
