from . import db


class Certificate(db.Model):
    __tablename__ = "certificates"
    id = db.Column(db.Integer, primary_key=True)
    public_key = db.Column(db.Text)
    private_key = db.Column(db.Text)
    cn = db.Column(db.String(64))
    san = db.Column(db.String(64))
