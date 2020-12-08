from . import db


class Certificate(db.Model):
    __tablename__ = "certificates"
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.Text)
    private_key = db.Column(db.Text)
    subject = db.Column(db.String(64))
    not_valid_before = db.Column(db.DateTime)
    not_valid_after = db.Column(db.DateTime)
    template_id = db.Column(db.Integer, db.ForeignKey("templates.id"))
    issuer_id = db.Column(db.Integer, db.ForeignKey("certificates.id"), nullable=False)
    issuer = db.relationship("Certificate", remote_side=[id])
    ca = db.Column(db.Boolean)


class Template(db.Model):
    __tablename__ = "templates"
    id = db.Column(db.Integer, primary_key=True)
    key_usage = db.Column(db.String)
    certificates = db.relationship("Certificate", backref="template")
