"""
Testing company model
"""

import unittest
from app import create_app, db
from app.models import Company, User, Role, Boiler


class CompanyModelTestCase(unittest.TestCase):
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

    def test_company_user_access(self):
        c1 = Company(company_name="Company1")
        c2 = Company(company_name="Company2")
        db.session.add(c1)
        db.session.add(c2)
        r = Role.query.filter_by(name='Repr').first()
        u1 = User(email='repr1@example.com', password='cat', role=r, company=c1)
        u2 = User(email='repr2@example.com', password='cat', role=r, company=c2)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(u1.company_access(c1.id))
        self.assertFalse(u1.company_access(c2.id))
        self.assertTrue(u2.company_access(c2.id))
        self.assertFalse(u2.company_access(c1.id))

    def test_company_inspector_access(self):
        c1 = Company(company_name="Company1")
        c2 = Company(company_name="Company2")
        r = Role.query.filter_by(name='Inspector').first()
        u1 = User(email='inspector1@example.com', password='cat', role=r, company=c1)
        self.assertTrue(u1.company_access(c1.id))
        self.assertTrue(u1.company_access(c2.id))

    def test_company_admin_access(self):
        c1 = Company(company_name="Company1")
        c2 = Company(company_name="Company2")
        r = Role.query.filter_by(name='Administrator').first()
        u1 = User(email='admin1@example.com', password='cat', role=r, company=c2)
        self.assertTrue(u1.company_access(c1.id))
        self.assertTrue(u1.company_access(c2.id))

    def test_boiler_user_access(self):
        c1 = Company(company_name="Company1")
        c2 = Company(company_name="Company2")
        db.session.add(c1)
        db.session.add(c2)
        b1 = Boiler(boiler_name="Boiler1", company=c1)
        b2 = Boiler(boiler_name="Boiler2", company=c2)
        b3 = Boiler(boiler_name="Boiler3", company=c2)
        db.session.add(b1)
        db.session.add(b2)
        db.session.add(b3)
        db.session.commit()
        r = Role.query.filter_by(name='Repr').first()
        u1 = User(email='repr1@example.com', password='cat', role=r, company=c1)
        u2 = User(email='repr2@example.com', password='cat', role=r, company=c2)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertTrue(u1.boiler_access(b1.id))
        self.assertFalse(u1.boiler_access(b2.id))
        self.assertFalse(u1.boiler_access(b3.id))
        self.assertFalse(u2.boiler_access(b1.id))
        self.assertTrue(u2.boiler_access(b2.id))
        self.assertTrue(u2.boiler_access(b3.id))



