from flask import jsonify, json, g
from .. import db
from ..models import Company, Permission, User, Boiler, Node, Measurement, Norm
from . import api
from .errors import forbidden
from .decorators import permission_required


@api.route('/default_structure')
@permission_required(Permission.CREATE_BOILER)
def structure():
    """
    Provides default boiler structure as json
    :return: json
    """
    with open('app/static/default_nodes.json', 'r') as file_obj:
        default_boiler_structure = json.load(file_obj)
    return jsonify(default_boiler_structure)


