from flask import render_template, session, redirect, url_for, current_app, flash, abort
from flask_login import login_required, current_user
from . import boiler
from .forms import CreateBoilerForm, AddNodeForm, CreateBoilerNodesForm
from .. import db
from ..models import User, Company, Role, Boiler, Permission, Node
from ..decorators import permission_required
import json


from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, FieldList, FormField


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
        return redirect(url_for("boiler.add_nodes", id=new_boiler.id))
    return render_template("boiler/create_boiler.html", form=form)


@boiler.route('<int:id>/add-nodes', methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def add_nodes(id):
    boiler_id = id
    with open('app/static/default_nodes.json', 'r') as f:
        structure = json.load(f)

    form = CreateBoilerNodesForm()
    if form.validate_on_submit():
        for block in structure:
            new_block = Node(boiler_id=boiler_id,
                             index=block.get('index'),
                             node_name=block.get('node_name')
                             )
            db.session.add(new_block)
            db.session.commit()
            db.session.expire_all()

            for child_1 in block.get('children'):
                new_child_1 = Node(boiler_id=boiler_id,
                                   parent_id=new_block.id,
                                   index=child_1.get('index'),
                                   node_name=child_1.get('node_name')
                                   )
                db.session.add(new_child_1)
                db.session.commit()
                db.session.expire_all()

                for child_2 in child_1.get('children'):
                    new_child_2 = Node(boiler_id=boiler_id,
                                       parent_id=new_child_1.id,
                                       index=child_2.get('index'),
                                       node_name=child_2.get('node_name')
                                       )
                    db.session.add(new_child_2)
                    db.session.commit()
                    db.session.expire_all()

                    elements = child_2.get("Elements")
                    points = child_2.get("Points")

                    for element in range(1, elements+1):
                        for point in range(1, points+1):
                            new_point = Node(boiler_id=boiler_id,
                                             parent_id=new_child_2.id,
                                             index=point,
                                             node_name='Element '+ str(element) + ' Point ' + str(point)
                                             )
                            db.session.add(new_point)
                            db.session.commit()
                            db.session.expire_all()
        flash("Nodes created")
        return redirect(url_for("boiler.show_boiler", id=boiler_id))

    return render_template('boiler/add_nodes.html', id=id, form=form, structure=structure)


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
    form = CreateBoilerForm(boiler=boiler)
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








