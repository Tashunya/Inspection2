from flask import render_template, session, redirect, url_for, current_app, flash, abort
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Company, Role, Permission
from ..decorators import permission_required


@main.route('/')
@login_required
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


@main.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.position = form.position.data
        current_user.contact_number = form.contact_number.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', id=current_user.id))
    form.username.data = current_user.username
    form.position .data = current_user.position
    form.contact_number.data = current_user.contact_number
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.USER_REGISTER)
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.company = Company.query.get(form.company.data)
        user.position = form.position.data
        user.contact_number = form.contact_number.data
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for('.user', id=id))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role
    form.company.data = user.company
    form.position.data = user.position
    form.contact_number.data = user.contact_number
    return render_template('edit_profile.html', form=form, user=user)
