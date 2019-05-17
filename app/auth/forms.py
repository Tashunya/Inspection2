from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, Role

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Length(min=6, max=64), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=64), Email()])
    username = StringField('Full Name', validators=[DataRequired(), Length(min=6, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    role = SelectField(u"Role", choices=[("admin", "Administrator"), ("inspector", "Inspector"), ("user", "User")], validators=[DataRequired()])
    company = SelectField(u"Company", choices=[("SYK","Mondi SYK"), ("Steti","Mondi Steti"), ("IP", "International Paper")], validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    # def validate_username(self, field):
    #     if User.query.filter_by(username=field.data).first():
    #         raise ValidationError('Username already in use.')