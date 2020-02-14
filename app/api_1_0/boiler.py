"""
This module is used to provide data to serve boiler views and js scripts.
"""

from flask import jsonify, json, request, url_for
from ..models import Permission, Node, Measurement, Norm
from . import api
from .. import db
from .decorators import permission_required
from .analysis import get_analysis_data


@api.route('/default_structure')
@permission_required(Permission.CREATE_BOILER)
def structure():
    """
    Provides default boiler structure as json
    :return: json {'structure': }
    """
    with open('app/static/basic_structure.json', 'r') as file_obj:
        default_boiler_structure = json.load(file_obj)
    return default_boiler_structure


@api.route('/children/<int:node_id>')
def children_level(node_id):
    """
    Provides list of children nodes of the given node as json
    :param node_id:
    :return: json [{id: , node_name: },]
    """
    node = Node.query.filter_by(id=node_id).first_or_404()
    children = node.get_children()
    return jsonify(children)


@api.route('analytics/<int:node_id>')
def analytics_data(node_id):
    """
    Provides measurements records info for chosen node for all years + norms info as json
    :param node_id:
    :return: {"avg_thickness": 0,
              "avg_thinning": 0,
              "last_year": 0,
              "stacked_bar": {
                  "labels": [],
                  "thickness": [],
                  "thinning": []},
              "pie": {}
              }
    """
    result = get_analysis_data(node_id)
    return jsonify(result)


@api.route('table/<int:node_id>')
def table_data(node_id):
    """
    Returns measurements records info for chosen node for all years + norms info as json
    :param node_id:
    :return: json
    """
    table_query = db.session.query(Node.node_name, Measurement.measure_date, Measurement.value,
                                   Norm.default, Norm.minor, Norm.major, Norm.defect). \
        outerjoin(Norm, Norm.node_id == Node.id). \
        outerjoin(Measurement, Measurement.node_id == Node.id). \
        filter(Node.parent_id == node_id). \
        filter(Measurement.value != None)

    table_dic = {}

    for current_node in table_query.all():
        year = current_node[1].year
        if str(year) not in table_dic:
            table_dic[str(year)] = []
        table_dic[str(year)].append(current_node)

    return jsonify(table_dic)


@api.route('/pagination/<int:node_id>')
@permission_required(Permission.CREATE_BOILER)
def get_pagination(node_id):
    """
    Returns json for pagination template
    :param node_id:
    :return:
    """
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
    prev = None
    if pagination_list.has_prev:
        prev = url_for('api.get_pagination', page=page-1, node_id=node_id)
    next = None
    if pagination_list.has_next:
        next = url_for('api.get_pagination', page=page+1, node_id=node_id)
    return jsonify({
        'rows': [row for row in rows],
        'prev': prev,
        'next': next,
        'count': pagination_list.total,
        'node_id': node_id
    })
