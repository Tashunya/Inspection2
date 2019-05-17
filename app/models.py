from . import db
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class Company(db.Model):
    __tablename__ = 'companies'
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(64), unique=True, index=True)
    users = db.relationship('User', backref='company', lazy='dynamic')
    boilers = db.relationship('Boiler', backref='company', lazy='dynamic')

    def __repr__(self):
        return '<Company %r>' % self.company_name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    contact_number = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    def __repr__(self):
        return '<User %r>' % self.username

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Boiler(db.Model):
    __tablename__ = 'boilers'
    id = db.Column(db.Integer, primary_key=True)
    boiler_name = db.Column(db.String(64), unique=True, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))

    def __repr__(self):
        return '<Boiler %r>' % self.boiler_name




# # db.create_all()
# admin_role = Role(name="Admin")
# user_role = Role(name="User")
# user_john = User(username ="john", role=admin_role)
# user_susan = User(username="susan", role=user_role)
#
# # db.session.add_all([admin_role, user_role, user_john, user_susan])
# # db.session.commit()



