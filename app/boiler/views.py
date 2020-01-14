"""
This module is used to manage boiler routes.
"""

from flask import render_template, redirect, url_for, flash, abort, json, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from . import boiler
from .. import db
from ..models import Company, Boiler, Permission, Node, Norm, Measurement
from .forms import CreateBoilerForm, CreateBoilerNodesForm, NodeSelectForm, UploadForm
from .auxiliary import add_nodes_to_db, allowed_file, get_analysis_data
from ..decorators import permission_required

# =====================================================
# BOILER ROUTES
# =====================================================


@boiler.route('/create', methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def create_boiler():
    """
    Manages route for the page where new boiler is created.
    :return:
    """
    form = CreateBoilerForm()
    if form.validate_on_submit():
        new_boiler = Boiler(boiler_name=form.boiler_name.data,
                            company_id=int(form.company.data))
        db.session.add(new_boiler)
        db.session.commit()
        flash("New boiler created")
        return redirect(url_for("boiler.add_nodes", boiler_id=new_boiler.id))
    return render_template("boiler/create_boiler.html", form=form)


@boiler.route('<int:boiler_id>/add-nodes', methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def add_nodes(boiler_id):
    """
    Manages route for the page where boiler nodes are created.
    :param boiler_id:
    :return:
    """
    with open('app/static/default_nodes.json', 'r') as structure_file:
        default_structure = json.load(structure_file)

    form = CreateBoilerNodesForm()

    if request.method == 'POST':
        updated_structure = request.get_json()['structure']
        add_nodes_to_db(updated_structure, boiler_id)
        flash("Nodes created")
        # return render_template("boiler/show_boiler.html", boiler_id=boiler_id)

    return render_template('boiler/add_nodes.html', id=boiler_id,
                           form=form, structure=default_structure)


@boiler.route('/<int:boiler_id>')
@login_required
def show_boiler(boiler_id):
    """
     Manages route for the page where boiler info is shown.
    :param boiler_id:
    :return:
    """
    requested_boiler = Boiler.query.filter_by(id=boiler_id).first_or_404()
    if not current_user.company_access(requested_boiler.company_id):
        abort(403)
    company = Company.query.filter_by(id=requested_boiler.company_id).first()
    form = NodeSelectForm(boiler_id=boiler_id)
    return render_template('boiler/show_boiler.html', boiler=requested_boiler,
                           company=company, form=form)


@boiler.route('/edit-boiler/<boiler_id>', methods=["GET", "POST"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def edit_boiler(boiler_id):
    """
     Manages route for the page where boiler info is edited.
    :param boiler_id:
    :return:
    """
    requested_boiler = Boiler.query.get_or_404(boiler_id)
    form = CreateBoilerForm(boiler=requested_boiler)
    if form.validate_on_submit():
        requested_boiler.boiler_name = form.boiler_name.data
        requested_boiler.company = Company.query.get(form.company.data)
        db.session.add(requested_boiler)
        db.session.commit()
        flash("The boiler has been updated.")
        return redirect(url_for('boiler.show_boiler', boiler_id=boiler_id))
    form.boiler_name.data = requested_boiler.boiler_name
    form.company.data = requested_boiler.company
    return render_template('boiler/edit_boiler.html', boiler=requested_boiler, form=form)


@boiler.route("/upload", methods=["GET", "POST"])
@login_required
@permission_required(Permission.BOILER_DATA_UPLOAD)
def upload():
    """
     Manages route for the page where measurement info for chosen node is uploaded to db.
    :return:
    """
    form = UploadForm()

    parent_id = int(request.args["parent_id"])
    node = Node.query.filter_by(id=parent_id).first()
    children = node.get_children()
    boiler_id = node.boiler.id
    inspector_id = current_user.id

    if request.method == "POST":
        date = form.year
        year = date.data.year

        file = request.files['upload']
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('boiler.upload', parent_id=parent_id))
        # check extension
        if not allowed_file(file.filename):
            flash("Incorrect file extension. You should upload CSV files only.")
            return redirect(url_for('boiler.upload', parent_id=parent_id))
        # filename = secure_filename(file.filename)

        data = file.read().decode('utf-8')
        data = data.strip("\r\n").rsplit('\r\n')
        data = [float(b) for a, b in (row.rsplit(',') for row in data)]

        # check number of data from csv file
        if len(data) != len(children):
            flash("Incorrect number of measurement points in file. Please, upload another file.")
            return redirect(url_for('boiler.upload', parent_id=parent_id))

        # check outliers
        norm = Norm.query.filter_by(node_id=children[0]['id']).first()
        for val in data:
            if val > norm.default + 0.1:  # 0.1 - допустимое превышение заводской толщины
                flash("Abnormal data.")
                return redirect(url_for('boiler.upload', parent_id=parent_id))

        # delete old values if any
        for child in children:
            Measurement.query.filter_by(node_id=child["id"]).\
                filter(extract("year", Measurement.measure_date) == year).\
                delete(synchronize_session=False)

        # save new values
        for child, val in zip(children, data):
            new_measurement = Measurement(inspector_id=inspector_id,
                                          node_id=child["id"],
                                          value=val,
                                          measure_date=date.data)
            db.session.add(new_measurement)
        db.session.commit()

        flash("Data uploaded")
        return redirect(url_for("boiler.show_boiler", boiler_id=boiler_id))

    return render_template('boiler/upload.html', form=form)


@boiler.route("/analytics")
@login_required
def analytics():
    """
    Manage route for the analytics page.
    :return:
    """
    parent_id = int(request.args["parent_id"])
    boiler = Node.query.filter_by(id=parent_id).first().boiler
    company = boiler.company
    level_2_node = Node.query.filter_by(id=parent_id).first()
    level_1_node = level_2_node.ParentNode
    block = level_1_node.ParentNode
    element_name = [block.node_name, level_1_node.node_name, level_2_node.node_name]
    return render_template('boiler/analytics.html', parent_id=parent_id,
                           boiler=boiler, company=company, element_name=element_name)


# try pagination
@boiler.route('/pagination/<int:node_id>', methods=["GET"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def pagination(node_id):
    """
    Manage route for the page with boiler node info using pagination
    :param node_id:
    :return:
    """
    requested_node = Node.query.get_or_404(node_id)
    requested_boiler = requested_node.boiler
    page = request.args.get('page', 1, type=int)

    table_query = db.session.query(Node.node_name, Node.index, Measurement.measure_date,
                                   Measurement.value, Norm.default,
                                   Norm.minor, Norm.major, Norm.defect). \
        outerjoin(Norm, Norm.node_id == Node.id). \
        outerjoin(Measurement, Measurement.node_id == Node.id). \
        filter(Node.parent_id == node_id). \
        filter(Measurement.value != None)

    pagination_list = table_query.paginate(page, per_page=10, error_out=False)
    rows = pagination_list.items

    return render_template('boiler/pagination.html', rows=rows, pagination=pagination_list,
                           node_id=node_id, boiler=requested_boiler, element=requested_node)


@boiler.route('/children/<node>', methods=["GET"])
@login_required
def level(node):
    """
    Provide children nodes of the give node as json
    :param node:
    :return: json
    """
    node = Node.query.filter_by(id=node).first_or_404()
    children = node.get_children()
    return jsonify(children)


@boiler.route('/table/<node>', methods=["GET"])
@login_required
def table(node):
    """
    Return measurements records info for chosen node for all years + norms info as json
    :param node:
    :return: json
    """
    table_query = db.session.query(Node.node_name, Measurement.measure_date, Measurement.value,
                                   Norm.default, Norm.minor, Norm.major, Norm.defect). \
        outerjoin(Norm, Norm.node_id == Node.id). \
        outerjoin(Measurement, Measurement.node_id == Node.id). \
        filter(Node.parent_id == node). \
        filter(Measurement.value != None)

    table_dic = {}

    for current_node in table_query.all():
        year = current_node[1].year
        if str(year) not in table_dic:
            table_dic[str(year)] = []
        table_dic[str(year)].append(current_node)

    return jsonify(table_dic)


@boiler.route('/analytics/<int:node_id>', methods=["GET"])
@login_required
def analytics_data(node_id):
    """
    Provide measurements records info for chosen node for all years + norms info as json
    :param node_id:
    :return: json
    """
    result = get_analysis_data(node_id)

    return jsonify(result)
