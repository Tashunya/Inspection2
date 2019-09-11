"""
This module is used to provide data to serve boiler views and js scripts.
"""

from flask import jsonify, json
from ..models import Permission, Node
from . import api
from .decorators import permission_required
from .analysis import get_analysis_data


@api.route('/default_structure')
@permission_required(Permission.CREATE_BOILER)
def structure():
    """
    Provides default boiler structure as json
    :return: json {'structure': }
    """
    with open('app/static/default_nodes.json', 'r') as file_obj:
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
