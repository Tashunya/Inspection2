#!/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Role, Permission, Company, Boiler, Node, Norm, Measurement
from flask_migrate import Migrate, upgrade

app = create_app(os.getenv("FLASK_CONFIG") or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Company=Company,
                Boiler=Boiler, Node=Node, Norm=Norm, Measurement=Measurement)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command()
def deploy():
    # migrate db to latest revision
    upgrade()
    # create user roles
    Role.insert_roles()
