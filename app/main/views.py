from flask import render_template, session, redirect, url_for, current_app, flash, abort
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, CompanyRegistrationForm, EditCompanyForm
from .. import db
from ..models import User, Company, Role, Boiler, Permission
from ..decorators import permission_required


# =========================================
# INDEX ROUTES
# =========================================


@main.route('/')
@login_required
def index():
    if current_user.role.name == "Inspector":
        return redirect(url_for('.inspector'))
    if current_user.role.name == "Administrator":
        return redirect(url_for('.admin'))
    company = Company.query.filter_by(id=current_user.company_id).first()
    boilers = Boiler.query.filter_by(company_id=current_user.company_id).all()
    return render_template('index.html', company=company, boilers=boilers)


@main.route('/inspector')
@login_required
def inspector():
    if current_user.role.name == "Inspector":
        company_list = Company.query.order_by(Company.company_name).all()
        return render_template('inspector.html', company_list=company_list)
    else:
        abort(403)


@main.route('/admin')
@login_required
def admin():
    if current_user.role.name == "Administrator":
        company_list = Company.query.order_by(Company.company_name).all()
        return render_template('inspector.html', company_list=company_list)
    else:
        abort(403)


# ====================================
# USER ROUTES
# ====================================


@main.route('/user/<int:id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    if not current_user.company_access(user.company_id):
        abort(403)
    company = Company.query.filter_by(id=current_user.company_id).first()
    role = Role.query.filter_by(id=current_user.role_id).first()
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
        user.role = Role.query.get(form.role.data.id)
        user.company = Company.query.get(form.company.data.id)
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


# ============================================
# COMPANY ROUTES
# ============================================


@main.route('/register-company', methods=["GET", "POST"])
@login_required
@permission_required(Permission.COMPANY_REGISTER)
def register_company():
    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        company = Company(company_name=form.company_name.data,
                    location=form.location.data,
                    about=form.about.data)
        db.session.add(company)
        db.session.commit()
        flash("New company registered")
        return redirect(url_for(".index"))
    return render_template("register_company.html", form=form)


@main.route('/company/<int:id>')
@login_required
def company(id):
    if not current_user.company_access(id):
        abort(403)
    company = Company.query.filter_by(id=id).first_or_404()
    employees = User.query.filter_by(company_id=id).order_by(User.username).all()
    boilers = Boiler.query.filter_by(company_id=id).all()
    return render_template('company.html', company=company, employees=employees, boilers=boilers)


@main.route('/edit-company/<int:id>', methods=["GET", "POST"])
@login_required
@permission_required(Permission.COMPANY_REGISTER)
def edit_company(id):
    company = Company.query.get_or_404(id)
    form = EditCompanyForm(company=company)
    if form.validate_on_submit():
        company.company_name = form.company_name.data
        company.location = form.location.data
        company.about = form.about.data
        db.session.add(company)
        db.session.commit()
        flash("The company profile has been updated.")
        return redirect(url_for('.company', id=id))
    form.company_name.data = company.company_name
    form.location.data = company.location
    form.about.data = company.about
    return render_template('edit_company.html', form=form, company=company)


