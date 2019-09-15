from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, ValidationError
from wtforms_alchemy import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, Optional
from ..models import Role, User, Company


class EditProfileForm(FlaskForm):
    username = StringField('Full Name', validators=[Length(min=0, max=64)])
    position = StringField('Position', validators=[Length(min=0, max=64)])
    contact_number = StringField("Contact Number", validators=[Length(min=0, max=64)])
    submit = SubmitField('Edit Profile')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(min=6, max=64), Email()])
    username = StringField('Full Name', validators=[DataRequired(), Length(min=6, max=64)])
    confirmed = BooleanField('Confirmed')
    role = QuerySelectField("Role", allow_blank=True, get_label='name')
    company = QuerySelectField("Company", allow_blank=True, get_label='company_name')
    position = StringField('Position', validators=[Length(min=0, max=64)])
    contact_number = StringField('Contact Number', validators=[Length(min=0, max=64)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.query_factory = lambda: Role.query.order_by(Role.id)
        self.company.query_factory = lambda: Company.query.order_by(Company.company_name)
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class CompanyRegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=6, max=64)])
    location = StringField('Location', validators=[Length(min=0, max=64)])
    about = TextAreaField('Info', validators=[Optional()])
    submit = SubmitField('Register Company')


class EditCompanyForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=6, max=64)])
    location = StringField('Location', validators=[Length(min=0, max=64)])
    about = TextAreaField('Info', validators=[Optional()])
    submit = SubmitField('Edit Company')
