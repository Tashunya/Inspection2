from flask import Blueprint

boiler = Blueprint('boiler', __name__)

from . import views, errors
