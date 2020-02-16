from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User, Permission
from ..decorators import permission_required
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
from ..email import send_email


@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            flash('You were successfully logged in')
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))


@auth.route("/register-user", methods=["GET", "POST"])
@login_required
@permission_required(Permission.USER_REGISTER)
def register_user():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    role_id=int(form.role.data.id),
                    company_id=int(form.company.data.id),
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "Finish Registration",
                   'auth/email/confirm', user=user, token=token)
        flash("User created. A letter have been sent to finish registration.")
        return redirect(url_for("main.user", id=user.id))
    return render_template("auth/register_user.html", form=form)


@auth.route("/confirm/<token>", methods=["GET", "POST"])
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash("You have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired.")
    return redirect(url_for('main.index'))


@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "Account Confirmation",
               "auth/email/confirm", user=current_user,
               token=token)
    flash("A new confirmation email has been sent to you by email.")
    return redirect(url_for('main.index'))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your password has been updated")
            return redirect(url_for('main.user'))
        else:
            flash("Invalid password.")
    return render_template("auth/change_password.html", form=form)
