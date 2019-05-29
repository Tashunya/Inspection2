from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, Optional
from wtforms import ValidationError
from ..models import Role, User, Company


class CreateBoilerForm(FlaskForm):
    boiler_name = StringField('Boiler Name', validators=[DataRequired(), Length(min=3, max=64)])
    company = SelectField("Company", coerce=int)
    submit = SubmitField('Create Boiler')

    def __init__(self, *args, **kwargs):
        super(CreateBoilerForm, self).__init__(*args, **kwargs)
        self.company.choices = [(company.id, company.company_name) for company in Company.query.all()]


# class EditBoilerForm(FlaskForm):
#     boiler_name = StringField('Boiler Name', validators=[DataRequired(), Length(min=3, max=64)])
#     company = SelectField("Company", coerce=int)
#     submit = SubmitField('Edit Boiler')
#
#     def __init__(self, boiler, *args, **kwargs):
#         super(EditBoilerForm, self).__init__(*args, **kwargs)
#         self.company.choices = [(company.id, company.company_name) for company in Company.query.all()]
#         self.boiler = boiler


class AddNodeForm(FlaskForm):
    # boiler_id = IntegerField("Boiler ID", default=1, validators=[DataRequired()])
    node_name = StringField("Node Name", validators=[Length(min=3, max=64)])
    parent_id = IntegerField("Parent ID", validators=[Optional()])
    submit = SubmitField("Add Node")


class CreateBoilerNodesForm(FlaskForm):
    submit = SubmitField("Add Nodes")