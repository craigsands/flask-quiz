from flask import render_template, redirect, request, session, url_for
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user
from app.auth import bp
from app.auth.forms import LoginForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    #if current_user.is_authenticated:
    if session.get('username'):
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        #login_user(user)
        session['username'] = form.username.data
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form, session=session)


@bp.route('/logout')
def logout():
    #logout_user()
    session.pop('username', None)
    return redirect(url_for('main.index'))
