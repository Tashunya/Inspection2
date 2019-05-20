from flask import render_template, session, redirect, url_for, current_app, flash
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Company


@main.route('/')
def index():
    company = Company.query.filter_by(id=current_user.company_id).first()
    return render_template('index.html', company = company)

@main.route('/user/<username>')
@login_required
def account():
    return render_template('user.html')
