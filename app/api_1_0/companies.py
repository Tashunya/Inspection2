"""
This module is used to provide data to serve main views
"""

from flask import jsonify, g
from ..models import Company, Permission, User, Boiler
from . import api
from .errors import forbidden
from .decorators import permission_required


# FOR ADMINS AND MODERATORS
@api.route('/companies/')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_companies():
    """
    Provides list of all companies
    :return: {companies: [{about: , company_name: , location: }, ]
    """
    companies = Company.query.all()
    return jsonify({'companies': [company.to_json() for company in companies]})


@api.route('/companies/<int:company_id>')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_company(company_id):
    """
    Provides information about one company
    :param company_id:
    :return:
    """
    company = Company.query.get_or_404(company_id)
    return jsonify({'company': company.to_json()})


@api.route('/boilers/')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_boilers():
    """
    Provides list of all boilers
    :return: {boilers: [{boiler_id: , company_name: , location: }, ]
    """
    boilers = Boiler.query.all()
    return jsonify({'boilers': [boiler.to_json() for boiler in boilers]})


@api.route('/boilers/<int:boiler_id>')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_boiler(boiler_id):
    """
    Provides information about one boiler
    :param boiler_id:
    :return:
    """
    boiler = Boiler.query.get_or_404(boiler_id)
    return jsonify({'boiler': boiler.to_json()})


@api.route('/users/<int:user_id>')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_user(user_id):
    """
    Provides information about one user
    :param user_id:
    :return:
    """
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_json()})


# FOR USERS
@api.route('/company/')
def get_user_company():
    """
    Provides information about current user's company
    :return: json with company or 404
    """
    company = g.current_user.company
    return jsonify({'company': company.to_json()})


@api.route('/company/boilers')
def get_company_boilers():
    """
    Provides information about current user's company's boilers
    :return: json
    """
    company = g.current_user.company
    boilers = company.boilers.order_by(Boiler.boiler_name)
    return jsonify({'boilers': [boiler.to_json() for boiler in boilers]})


@api.route('/company/boilers/<int:boiler_id>')
def get_company_boiler(boiler_id):
    """
    Provides information about current user's company's boiler
    :param boiler_id:
    :return: json
    """
    boiler = Boiler.query.get_or_404(boiler_id)
    if not g.current_user.boiler_access(boiler_id):
        return forbidden('Insufficient permissions')
    return jsonify({'boiler': boiler.to_json()})


@api.route('/company/users')
def get_company_users():
    """
    Provides information about current user's company's users
    :return: json
    """
    users = g.current_user.company.users.order_by(User.username)
    return jsonify({'users': [user.to_json() for user in users]})
