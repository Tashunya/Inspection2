from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin, AnonymousUserMixin
from . import db, login_manager


class Permission:
    OWN_BOILER_ACCESS = 1
    ALL_BOILERS_ACCESS = 2
    BOILER_DATA_UPLOAD = 4
    USER_REGISTER = 8
    REPORT_DOWNLOAD = 16
    EDIT_BOILER_DATA = 32
    COMPANY_REGISTER = 64
    CREATE_BOILER = 128
    VIEW_PROFILES = 256


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

#==========================================


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

    # def is_administrator(self):
    #     return self.can(Permission.ADMIN)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ============================================

class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(64), unique=True, index=True)
    users = db.relationship('User', backref='company', lazy='dynamic')
    boilers = db.relationship('Boiler', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<Company %r>' % self.company_name

class Boiler(db.Model):
    __tablename__ = 'boilers'
    id = db.Column(db.Integer, primary_key=True)
    boiler_name = db.Column(db.String(64), unique=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    def __repr__(self):
        return '<Boiler %r>' % self.boiler_name




# db.create_all()
# admin_role = Role(name="Admin")
# user_role = Role(name="User")
# user_john = User(username ="john", role=admin_role)
# user_susan = User(username="susan", role=user_role)
#
# # db.session.add_all([admin_role, user_role, user_john, user_susan])
# # db.session.commit()



