from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms_alchemy import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import ValidationError
from ..models import User, Role, Company


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(min=6, max=64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=64), Email()])
    username = StringField('Full Name', validators=[DataRequired(), Length(min=6, max=64)])
    role = QuerySelectField("Role", allow_blank=True, get_label='name')
    company = QuerySelectField("Company", allow_blank=True, get_label='company_name')
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.role.query_factory = lambda: Role.query.order_by(Role.id)
        self.company.query_factory = lambda: Company.query.order_by(Company.company_name)

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField('New password',
                             validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update password')