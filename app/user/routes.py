from flask import request, render_template, url_for
from flask_login import login_required
from app.user import bp
from app.models import User
from app.tables import SortableUserTable


@bp.route('/')
@login_required
def index():
    items_per_page = 10
    sort = request.args.get('sort', 'id')
    order = request.args.get('direction', 'asc')
    reverse = (order == 'desc')
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(
        getattr(getattr(User, sort), order)()
    ).paginate(page, items_per_page, False)
    first_url = url_for('users.index', page=1) \
        if users.has_prev else None
    prev_url = url_for('users.index', page=users.prev_num) \
        if users.has_prev else None
    next_url = url_for('users.index', page=users.next_num) \
        if users.has_next else None
    last_url = url_for('users.index', page=users.pages) \
        if users.has_next else None
    return render_template('user/index.html', title='Users',
                           table=SortableUserTable(
                               users.items, sort_by=sort,
                               sort_reverse=reverse),
                           first_url=first_url, prev_url=prev_url,
                           next_url=next_url, last_url=last_url)


@bp.route('/<username>')
@login_required
def get_info(username):
    user = User.query.filter_by(username=username).first()
    return render_template('user/info.html', title='User Info', user=user)
