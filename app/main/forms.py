from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email
from wtforms import ValidationError
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
    role = SelectField("Role", choices=[], coerce=int)
    company = SelectField("Company", choices=[], coerce=int)
    position = StringField('Position', validators=[Length(min=0, max=64)])
    contact_number = StringField('Contact Number', validators=[Length(min=0, max=64)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.company.choices = [(company.id, company.company_name)
                                for company in Company.query.order_by(Company.company_name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

