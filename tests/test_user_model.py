import unittest
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser


class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        u = User(password = 'cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = User(password = 'cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password = 'cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_confirmation_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.OWN_BOILER_ACCESS))
        self.assertFalse(u.can(Permission.ALL_BOILERS_ACCESS))
        self.assertFalse(u.can(Permission.BOILER_DATA_UPLOAD))
        self.assertFalse(u.can(Permission.USER_REGISTER))
        self.assertFalse(u.can(Permission.REPORT_DOWNLOAD))
        self.assertFalse(u.can(Permission.EDIT_BOILER_DATA))
        self.assertFalse(u.can(Permission.CREATE_BOILER))
        self.assertFalse(u.can(Permission.VIEW_PROFILES))

    def test_user_admin(self):
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='admin@example.com', password='cat', role=r)
        self.assertFalse(u.can(Permission.OWN_BOILER_ACCESS))
        self.assertTrue(u.can(Permission.ALL_BOILERS_ACCESS))
        self.assertTrue(u.can(Permission.BOILER_DATA_UPLOAD))
        self.assertTrue(u.can(Permission.USER_REGISTER))
        self.assertTrue(u.can(Permission.REPORT_DOWNLOAD))
        self.assertTrue(u.can(Permission.EDIT_BOILER_DATA))
        self.assertTrue(u.can(Permission.CREATE_BOILER))
        self.assertTrue(u.can(Permission.VIEW_PROFILES))

    def test_user_inspector(self):
        r = Role.query.filter_by(name='Inspector').first()
        u = User(email='inspector@example.com', password='cat', role=r)
        self.assertFalse(u.can(Permission.OWN_BOILER_ACCESS))
        self.assertTrue(u.can(Permission.ALL_BOILERS_ACCESS))
        self.assertTrue(u.can(Permission.BOILER_DATA_UPLOAD))
        self.assertFalse(u.can(Permission.USER_REGISTER))
        self.assertTrue(u.can(Permission.REPORT_DOWNLOAD))
        self.assertTrue(u.can(Permission.EDIT_BOILER_DATA))
        self.assertFalse(u.can(Permission.CREATE_BOILER))
        self.assertTrue(u.can(Permission.VIEW_PROFILES))

    def test_user_repr(self):
        r = Role.query.filter_by(name='Repr').first()
        u = User(email='repr@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.OWN_BOILER_ACCESS))
        self.assertFalse(u.can(Permission.ALL_BOILERS_ACCESS))
        self.assertFalse(u.can(Permission.BOILER_DATA_UPLOAD))
        self.assertFalse(u.can(Permission.USER_REGISTER))
        self.assertTrue(u.can(Permission.REPORT_DOWNLOAD))
        self.assertFalse(u.can(Permission.EDIT_BOILER_DATA))
        self.assertFalse(u.can(Permission.CREATE_BOILER))
        self.assertFalse(u.can(Permission.VIEW_PROFILES))

