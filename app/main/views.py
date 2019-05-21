from flask import render_template, session, redirect, url_for, current_app, flash, abort
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import User, Company, Role


@main.route('/')
def index():
    company = Company.query.filter_by(id=current_user.company_id).first()
    role = Role.query.filter_by(id=current_user.role_id).first()
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    return render_template('index.html', company=company, role=role)

@main.route('/user/<id>')
@login_required
def user(id):
    company = Company.query.filter_by(id=current_user.company_id).first()
    role = Role.query.filter_by(id=current_user.role_id).first()

    user = User.query.filter_by(id=id).first_or_404()
    return render_template('user.html', user=user, company=company, role=role)
