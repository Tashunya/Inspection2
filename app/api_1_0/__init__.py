"""
This module is used to initiate api
"""

from flask import Blueprint

api = Blueprint('api', __name__)

from . import errors, authentication, companies, decorators, boiler
