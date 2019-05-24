from flask import render_template, session, redirect, url_for, current_app, flash, abort
from flask_login import login_required, current_user
from . import boiler
from .forms import CreateBoilerForm, EditBoilerForm
from .. import db
from ..models import User, Company, Role, Boiler, Permission
from ..decorators import permission_required


# =====================================================
# BOILER ROUTES
# =====================================================


@boiler.route('/create', methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def create_boiler():
    form = CreateBoilerForm()
    if form.validate_on_submit():
        new_boiler = Boiler(boiler_name=form.boiler_name.data,
                        company_id=int(form.company.data))
        db.session.add(new_boiler)
        db.session.commit()
        flash("New boiler created")
        return redirect(url_for("main.index"))
    return render_template("boiler/create_boiler.html", form=form)


@boiler.route('/<int:id>')
@login_required
def show_boiler(id):
    boiler = Boiler.query.filter_by(id=id).first_or_404()
    if not current_user.company_access(boiler.company_id):
        abort(403)
    company = Company.query.filter_by(id=boiler.company_id).first()
    return render_template('boiler/show_boiler.html', boiler=boiler, company=company)


@boiler.route('/edit-boiler/<id>', methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def edit_boiler(id):
    boiler = Boiler.query.get_or_404(id)
    form = EditBoilerForm(boiler=boiler)
    if form.validate_on_submit():
        boiler.boiler_name = form.boiler_name.data
        boiler.company = Company.query.get(form.company.data)
        db.session.add(boiler)
        db.session.commit()
        flash("The boiler has been updated.")
        return redirect(url_for('boiler.show_boiler', id=id))
    form.boiler_name.data = boiler.boiler_name
    form.company.data = boiler.company
    return render_template('boiler/edit_boiler.html', boiler=boiler, form=form)
