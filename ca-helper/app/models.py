from . import db


class Certificate(db.Model):
    __tablename__ = "certificates"
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.Text)
    private_key = db.Column(db.Text)
    cn = db.Column(db.String(64))
    san = db.Column(db.String(64))
    valid_from = db.Column(db.DateTime)
    valid_to = db.Column(db.DateTime)
    template_id = db.Column(db.Integer, db.ForeignKey("templates.id"))
    ca_id = db.Column(db.Integer, db.ForeignKey("certificates.id"))


class Template(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True)
    key_usage = db.Column(db.String)
    certificates = db.relationship('Certificate', backref='template')
