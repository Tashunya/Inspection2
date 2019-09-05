from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from sqlalchemy.orm import backref
from . import db, login_manager


class Permission:
    OWN_BOILER_ACCESS = 1 # доступ к своей компании и к своим котлам (возможно не нужно)
    ALL_BOILERS_ACCESS = 2 # доступ ко всем компаниям и котлам
    BOILER_DATA_UPLOAD = 4 # загрузка данных измерений ко всем котлам
    USER_REGISTER = 8 # создание и редактирование пользователей
    REPORT_DOWNLOAD = 16 # выгрузка отчетов по котлам
    EDIT_BOILER_DATA = 32 # редактирование данных по котлам (узлов, норм, измерений)
    COMPANY_REGISTER = 64 # регистрация и редактирование компаний (возможно перенос в USER_REGISTER?)
    CREATE_BOILER = 128 # создание карточки и структуры котла
    VIEW_PROFILES = 256 # просмотр всех профилей пользователей (возможно перенос в USER_REGISTER?)


# ==============================================
# ROLE

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'Repr': [Permission.OWN_BOILER_ACCESS, Permission.REPORT_DOWNLOAD],
            'Inspector': [Permission.ALL_BOILERS_ACCESS, Permission.BOILER_DATA_UPLOAD,
                          Permission.EDIT_BOILER_DATA, Permission.REPORT_DOWNLOAD,
                          Permission.VIEW_PROFILES],
            'Administrator': [Permission.ALL_BOILERS_ACCESS, Permission.BOILER_DATA_UPLOAD,
                              Permission.USER_REGISTER, Permission.REPORT_DOWNLOAD,
                              Permission.EDIT_BOILER_DATA, Permission.COMPANY_REGISTER,
                              Permission.CREATE_BOILER, Permission.VIEW_PROFILES]
        }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name


# ==========================================
# USER

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    contact_number = db.Column(db.String(64))
    position = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    users = db.relationship('Measurement', backref='inspector', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def company_access(self, company_id):
        if self.company_id == company_id or self.can(Permission.ALL_BOILERS_ACCESS):
            return True
        return False

    def boiler_access(self, boiler_id):
        boiler = Boiler.query.filter_by(id=boiler_id).first()
        if self.company_id == boiler.company_id or self.can(Permission.ALL_BOILERS_ACCESS):
            return True
        return False

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# =============================================
# COMPANY
# =============================================

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(64), unique=True, index=True)
    location = db.Column(db.String(64))
    about = db.Column(db.Text)
    users = db.relationship('User', backref='company', lazy='dynamic')
    boilers = db.relationship('Boiler', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<Company %r>' % self.company_name


# ============================================
# BOILER
# ============================================

class Boiler(db.Model):
    __tablename__ = 'boilers'
    id = db.Column(db.Integer, primary_key=True)
    boiler_name = db.Column(db.String(64), index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    nodes = db.relationship('Node', backref='boiler', lazy='dynamic')

    def __repr__(self):
        return '<Boiler %r>' % self.boiler_name


class Node(db.Model):  # все узлы и точки котла
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    boiler_id = db.Column(db.Integer, db.ForeignKey('boilers.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    index = db.Column(db.Integer)
    node_name = db.Column(db.String(64))
    picture = db.Column(db.LargeBinary)
    child_nodes = db.relationship('Node', backref=backref("ParentNode", remote_side=[id]), lazy='dynamic')
    norms = db.relationship("Norm", backref='node', lazy='dynamic')
    measurements = db.relationship("Measurement", backref='node', lazy='dynamic')

    def __repr__(self):
        return 'Node {}'.format(self.node_name)

    def as_dict(self):
        return {'id': self.id, 'node_name': self.node_name}


class Norm(db.Model):  # содержит нормативные значения для измерений всех точек
    __tablename__ = 'norms'
    id = db.Column(db.Integer, primary_key=True)
    default = db.Column(db.Float)
    minor = db.Column(db.Float)
    major = db.Column(db.Float)
    defect = db.Column(db.Float)
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))

    def __repr__(self):
        return 'Default {}'.format(self.default)

    def as_dict(self):
        return {"default": self.default, "defect": self.defect}


class Measurement(db.Model):  # фактические измерения
    __tablename__ = 'measurements'
    id = db.Column(db.Integer, primary_key=True)
    inspector_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    measure_date = db.Column(db.DateTime, default=datetime.utcnow)
    value = db.Column(db.Float)


