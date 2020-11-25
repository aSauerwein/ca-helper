from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, SelectField
from wtforms.validators import DataRequired


class CertificateForm(FlaskForm):
    CN = StringField("Subject Common Name", validators=[DataRequired()])
    SAN = TextField("Subject Alternative Name")
    CA = SelectField("Certificate Authority", choices=["a","b","c"])
    submit = SubmitField("Submit")
