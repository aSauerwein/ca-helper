from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField, SelectField
from wtforms.validators import DataRequired


class CertificateForm(FlaskForm):
    Country = StringField("Country")
    State_Provice = StringField("State or Provice")
    Locality = StringField("Locality")
    Organization = StringField("Organization")
    Common = StringField("Subject Common Name", validators=[DataRequired()])
    SAN = TextField("Subject Alternative Name")
    CA = SelectField("Certificate Authority")
    submit = SubmitField("Submit")
