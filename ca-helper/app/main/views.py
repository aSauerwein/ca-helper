from datetime import datetime
from flask import render_template, flash, session, redirect, url_for, request
from . import main
from .forms import CertificateForm
from .. import db
from ..models import Certificate
from pathlib import Path
from .crypto import create_key_pair
from cryptography.hazmat.primitives import serialization

root_key_path = Path("cfssl-ca/rootca.key")
root_crt_path = Path("flask-app/static/rootca.pem")


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/certificates", methods=["GET"])
def certificates():

    certs = Certificate.query.all()
    titles = [
        ("subject", "Subject"),
        ("not_valid_before", "Valid From"),
        ("not_valid_after", "Valid To"),
    ]
    return render_template("certificates.html", data=certs, titles=titles)


@main.route("/certificates/new", methods=["GET", "POST"])
def new_certificate():
    cert_form = CertificateForm()
    choices = ["self"]
    cas = Certificate.query.filter_by(ca=True).all()
    cert_form.CA.choices = choices
    if request.method == "POST":
        if cert_form.validate_on_submit():
            options = {}
            if request.form.get("CA") == "self":
                options["ca"] = True

            options["name"] = {
                "country": request.form.get("Country", ""),
                "state_provice": request.form.get("Country", ""),
                "locality": request.form.get("Country", ""),
                "organization": request.form.get("Country", ""),
                "common": request.form.get("Country", ""),
            }

            key, cert = create_key_pair(options)
            new_cert = Certificate(
                public_key=cert.public_bytes(serialization.Encoding.PEM),
                private_key=key,
                subject=str(cert.subject),
                not_valid_before=cert.not_valid_before,
                not_valid_after=cert.not_valid_after,
                ca=options.get("ca", False),
            )
            db.session.add(new_cert)
            db.session.commit()

            flash("certificate created", category="success")
        else:
            flash("something is wrong")
        return redirect(url_for(".certificates"))
    else:
        return render_template("new_certificate.html", form=cert_form)