from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Company, Permission, User, Boiler
from . import api
from .errors import forbidden
from .decorators import permission_required


# FOR ADMINS AND MODERATORS
@api.route('/companies/')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_companies():
    companies = Company.query.all()
    return jsonify({'companies': [company.to_json() for company in companies]})


@api.route('/boilers')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_boilers():
    boilers = Boiler.query.all()
    return jsonify({'boilers': [boiler.to_json() for boiler in boilers]})


@api.route('/companies/<int:company_id>')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_company(company_id):
    company = Company.query.filter_by(id=company_id).first()
    return jsonify({'company': company.to_json()})


@api.route('/boilers/<int:boiler_id>')
@permission_required(Permission.ALL_BOILERS_ACCESS)
def get_boiler(boiler_id):
    boiler = Boiler.query.filter_by(id=boiler_id).first()
    return jsonify({'boiler': boiler.to_json()})


# FOR USERS
@api.route('/company/')
def get_user_company():
    company_id = g.current_user.company.id
    company = Company.query.filter_by(id=company_id).first()
    return jsonify({'company': company.to_json()})


@api.route('/company/boilers')
def get_company_boilers():
    company_id = g.current_user.company.id
    boilers = Boiler.query.filter_by(company_id=company_id).all()
    return jsonify({'boilers': [boiler.to_json() for boiler in boilers]})


@api.route('/company/boilers/<int:boiler_id>')
def get_company_boiler(boiler_id):
    if g.current_user.boiler_access(boiler_id):
        boiler = Boiler.query.get_or_404(boiler_id)
        return jsonify({'boiler': boiler.to_json()})
    return forbidden('Insufficient permissions')


@api.route('/company/users')
def get_company_users():
    company_id = g.current_user.company.id
    users = User.query.filter_by(company_id=company_id).all()
    return jsonify({'users': [user.to_json() for user in users]})

