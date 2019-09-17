"""
This module is used to create forms for boiler pages.
"""
from datetime import datetime
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Length
from wtforms_alchemy import QuerySelectField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from ..models import Company, Node


class CreateBoilerForm(FlaskForm):
    """
    Form to create boiler.
    """
    boiler_name = StringField('Boiler Name', validators=[DataRequired(), Length(min=3, max=64)])
    company = SelectField("Company", coerce=int)
    submit = SubmitField('Create Boiler')

    def __init__(self, *args, **kwargs):
        super(CreateBoilerForm, self).__init__(*args, **kwargs)
        self.company.choices = [(company.id, company.company_name)
                                for company in Company.query.order_by(Company.company_name).all()
                                if company.company_name != "Inspection Company"]


class CreateBoilerNodesForm(FlaskForm):
    """
    Form to create boiler nodes.
    """
    submit = SubmitField("Add Nodes")


class NodeSelectForm(FlaskForm):
    """
    Form to select nodes.
    """
    block = QuerySelectField("Block", allow_blank=True, get_label='node_name')
    level_1 = SelectField("Level 1", choices=[], coerce=int)
    level_2 = SelectField("Level 2", choices=[], coerce=int)

    def __init__(self, *args, **kwargs):
        super(NodeSelectForm, self).__init__(*args, **kwargs)
        self.block.query_factory = lambda: Node.query. \
            filter_by(boiler_id=kwargs.get('boiler_id')).filter_by(parent_id=None)


class UploadForm(FlaskForm):
    """
    Form to upload file with measurements.
    """
    year = DateField(format='%Y-%m-%d', default=datetime.today, validators=[DataRequired()])
    upload = FileField('Upload CSV file', validators=[FileRequired()])
    submit = SubmitField("Upload")
