"""
Module is used to provide authentication for api
"""

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    """
    Verifies user email and password with token support
    :param email_or_token:
    :param password:
    :return: True or False
    """
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """
    Rejects in case of invalid credentials
    :return:
    """
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    """
    Rejects unconfirmed users for all the routes
    :return:
    """
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/tokens/', methods=["POST"])
def get_token():
    """
    Generates authentication token, rejects if user is anonymous or
    prevents using old tokens
    :return: token as json
    """
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600),
                    'expiration': 3600})
