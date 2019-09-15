"""
The module is used to handle errors for api
"""

from flask import jsonify


def forbidden(message):
    """
    Returns error response if route is forbidden
    :param message:
    :return:
    """
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def bad_request(message):
    """
    Returns error response if request is incorrect
    :param message:
    :return:
    """
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    """
    Returns error response if user is unauthorized
    :param message:
    :return:
    """
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response
