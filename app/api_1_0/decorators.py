"""
The module is used to handle access to api routes according to user permission
"""


from functools import wraps
from flask import g
from .errors import forbidden


def permission_required(permission):
    """
    Returns decorator that checks user permission
    :param permission:
    :return: decorator
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions")
            return f(*args, **kwargs)
        return decorated_function
    return decorator
