from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextField, SelectField, BooleanField
from wtforms.validators import DataRequired


class CertificateForm(FlaskForm):
    Country = StringField("Country", validators=[DataRequired()])
    State_Provice = StringField("State or Provice")
    Locality = StringField("Locality")
    Organization = StringField("Organization")
    Common = StringField("Subject Common Name", validators=[DataRequired()])
    SAN = TextField("Subject Alternative Name")
    Issuer = SelectField("Issuer")
    CA = BooleanField("CA Constraint", default=False)
    Validity = IntegerField("Validity in days", default=30)
    submit = SubmitField("Submit")
