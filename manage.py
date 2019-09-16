#!/usr/bin/env python

import os
from app import create_app, db
from app.models import User, Role, Permission, Company, Boiler, Node, Norm, Measurement
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand, upgrade

app = create_app(os.getenv("FLASK_CONFIG") or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Company=Company,
                Boiler=Boiler, Node=Node, Norm=Norm, Measurement=Measurement)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def deploy():
    # migrate db to latest revision
    upgrade()
    # create user roles
    Role.insert_roles()


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
