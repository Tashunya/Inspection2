from flask import render_template, session, redirect, url_for, current_app, flash, abort, json, jsonify, request
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import extract
from sqlalchemy.sql.expression import func
from datetime import datetime
from . import boiler
from .forms import CreateBoilerForm, CreateBoilerNodesForm, NodeSelectForm, UploadForm
from .. import db
from ..models import Company, Boiler, Permission, Node, Norm, Measurement
import csv


from ..decorators import permission_required

# =====================================================
# BOILER ROUTES
# =====================================================


@boiler.route('/create', methods=["GET", "POST"])  # create boiler
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


@boiler.route('<int:id>/add-nodes', methods=["GET", "POST"])  # add boiler structure and norms
@login_required
@permission_required(Permission.CREATE_BOILER)
def add_nodes(id):
    boiler_id = id
    with open('app/static/default_nodes.json', 'r') as f:
        default_structure = json.load(f)

    form = CreateBoilerNodesForm()

    if request.method == 'POST':
        updated_structure = request.get_json()['structure']
        add_nodes_to_db(updated_structure, boiler_id)
        flash("Nodes created")
        # return render_template("boiler/show_boiler.html", id=boiler_id)

    return render_template('boiler/add_nodes.html', id=id, form=form, structure=default_structure)


@boiler.route("/upload", methods=["GET", "POST"])  # add measurements for chosen node
@login_required
@permission_required(Permission.BOILER_DATA_UPLOAD)
def upload():
    form = UploadForm()
    parent_id = int(request.args["parent_id"])
    children = get_children(parent_id)
    boiler_id = get_boiler(parent_id)
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
        filename = secure_filename(file.filename)

        data = file.read().decode('utf-8')
        data = data.strip("\r\n").rsplit('\r\n')
        data = [ float(b) for a, b in (row.rsplit(',') for row in data) ]

        # check number of data from csv file
        if len(data) != len(children):
            flash("Incorrect number of measurement points in file. Please, upload another file.")
            return redirect(url_for('boiler.upload', parent_id=parent_id))

        # check outliers
        norm = Norm.query.filter_by(node_id=children[0]['id']).first()
        for val in data:
            if val > norm.default + 0.1: # 0.1 - допустимое превышение заводской (дефолтной) толщины стенки трубы
                flash("Abnormal data.")
                return redirect(url_for('boiler.upload', parent_id=parent_id))

        # # delete old values if any
        for node in children:
            Measurement.query.filter_by(node_id=node["id"]).\
                filter(extract("year", Measurement.measure_date) == year).\
                delete(synchronize_session=False)

        # save new values
        for node, val in zip(children, data):
            new_measurement = Measurement(inspector_id=inspector_id,
                                          node_id=node["id"],
                                          value=val,
                                          measure_date=date.data)
            db.session.add(new_measurement)
        db.session.commit()

        flash("Data uploaded")
        return redirect(url_for("boiler.show_boiler", id=boiler_id))

    return render_template('boiler/upload.html', form=form)


@boiler.route("/analytics")
@login_required
@permission_required(Permission.BOILER_DATA_UPLOAD)
def analytics():
    parent_id = int(request.args["parent_id"])
    children = get_children(parent_id)
    boiler_id = get_boiler(parent_id)
    return render_template('boiler/analytics.html')


@boiler.route('/<int:id>')  # show boiler info
@login_required
def show_boiler(id):
    boiler = Boiler.query.filter_by(id=id).first_or_404()
    if not current_user.company_access(boiler.company_id):
        abort(403)
    company = Company.query.filter_by(id=boiler.company_id).first()
    form = NodeSelectForm(boiler_id=boiler.id)
    return render_template('boiler/show_boiler.html', boiler=boiler, company=company, form=form)


@boiler.route('/edit-boiler/<id>', methods=["GET", "POST"])  # edit boiler info
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


# =============================
# AUXILIARY ROUTES
# =============================


@boiler.route('/default_structure', methods=["GET"])
@login_required
def structure():
    with open('app/static/default_nodes.json', 'r') as f:
        structure = json.load(f)
    return jsonify(structure)


@boiler.route('/children/<node>', methods=["GET", "POST"])  # get json with children nodes
@login_required
def level(node):
    level_array = get_children(node)
    return jsonify(level_array)


@boiler.route('/table/<node>', methods=["GET", "POST"])  # get json with measurements of chosen node
@login_required
def table(node):

    ''' SELECT nodes.id, nodes.node_name, measurements.measure_date, COALESCE(measurements.value, 0),
    norms."default", norms.minor, norms.major, norms.defect
    FROM public.nodes as nodes
    LEFT JOIN public.norms as norms
    ON nodes.id = norms.node_id
    LEFT JOIN public.measurements as measurements
    ON nodes.id = measurements.node_id
    WHERE parent_id = 3
    ORDER BY nodes.id; '''

    table_query = db.session.query(Node.node_name, Measurement.measure_date, Measurement.value, Norm.default, Norm.minor,
                         Norm.major, Norm.defect). \
        outerjoin(Norm, Norm.node_id == Node.id). \
        outerjoin(Measurement, Measurement.node_id == Node.id). \
        filter(Node.parent_id == node). \
        filter(Measurement.value != None).all()

    table_dic = {}

    for node in table_query:
        year = node[1].year
        if not str(year) in table_dic:
            table_dic[str(year)] = []
        table_dic[str(year)].append(node)

    return jsonify(table_dic)


# try pagination
@boiler.route('/pagination/<int:node_id>', methods=["GET"])
@login_required
@permission_required(Permission.CREATE_BOILER)
def pagination(node_id):
    boiler = db.session.query(Boiler.boiler_name).join(Node, Boiler.id == Node.boiler_id).filter(Node.id==node_id).first()[0]
    element = Node.query.filter_by(id=node_id).first().node_name
    page = request.args.get('page', 1, type=int)

    table_query = db.session.query(Node.node_name, Node.index, Measurement.measure_date, Measurement.value, Norm.default,
                                   Norm.minor,
                                   Norm.major, Norm.defect). \
        outerjoin(Norm, Norm.node_id == Node.id). \
        outerjoin(Measurement, Measurement.node_id == Node.id). \
        filter(Node.parent_id == node_id). \
        filter(Measurement.value != None)

    pagination = table_query.paginate(page, per_page=10, error_out=False)
    rows = pagination.items

    return render_template('boiler/pagination.html', rows=rows, pagination=pagination, node_id=node_id, boiler=boiler, element=element)

# =================================
# AUXILIARY FUNCTIONS
# =================================


def add_nodes_to_db(structure, boiler_id):

    last_id = db.session.query(func.max(Node.id)).first()[0]

    if last_id == None:
        current_id = 1
    else:
        current_id = last_id + 1

    for block in structure:
        new_block = Node(boiler_id=boiler_id,
                         index=block.get('index'),
                         node_name=block.get('node_name'),
                         id = current_id
                         )
        db.session.add(new_block)
        current_id += 1

        for child_1 in block.get('children'):
            new_child_1 = Node(boiler_id=boiler_id,
                               parent_id=new_block.id,
                               index=child_1.get('index'),
                               node_name=child_1.get('node_name'),
                               id = current_id
                               )
            db.session.add(new_child_1)
            current_id += 1

            for child_2 in child_1.get('children'):
                new_child_2 = Node(boiler_id=boiler_id,
                                   parent_id=new_child_1.id,
                                   index=child_2.get('index'),
                                   node_name=child_2.get('node_name'),
                                   id = current_id
                                   )
                db.session.add(new_child_2)
                current_id += 1

                elements = int(child_2.get("Elements"))
                points = int(child_2.get("Points"))

                for element in range(1, elements + 1):
                    for point in range(1, points + 1):
                        new_point = Node(boiler_id=boiler_id,
                                         parent_id=new_child_2.id,
                                         index=point,
                                         node_name='Element ' + str(element) + ' Point ' + str(point),
                                         id = current_id
                                         )
                        db.session.add(new_point)
                        new_point_norm = Norm(node_id=current_id,
                                              default=6.5,
                                              minor=6.0,
                                              major=5.2,
                                              defect=4.5)
                        db.session.add(new_point_norm)

                        current_id += 1
    db.session.commit()


def get_children(node):
    level_elements = Node.query.filter_by(parent_id=node).all()
    level_array = [element.as_dict() for element in level_elements]
    return level_array


def get_parent(node):
    node = Node.query.filter_by(id=node).first()
    parent_id = node.parent_id
    return parent_id


def get_boiler(node):
    node = Node.query.filter_by(id=node).first()
    boiler_id = node.boiler_id
    return boiler_id


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'csv'

















