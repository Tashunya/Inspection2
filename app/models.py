from . import db

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


# # db.create_all()
# admin_role = Role(name="Admin")
# user_role = Role(name="User")
# user_john = User(username ="john", role=admin_role)
# user_susan = User(username="susan", role=user_role)
#
# # db.session.add_all([admin_role, user_role, user_john, user_susan])
# # db.session.commit()



