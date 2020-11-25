from datetime import datetime
from flask import render_template, flash, session, redirect, url_for, request
from . import main
from .forms import CertificateForm
from .. import db
from ..models import Certificate
from pathlib import Path

root_key_path = Path("cfssl-ca/rootca.key")
root_crt_path = Path("flask-app/static/rootca.pem")


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/certificates", methods=["GET"])
def certificates():

    certs = Certificate.query.all()
    return render_template("certificates.html", data=certs)


@main.route("/certificates/new", methods=["GET", "POST"])
def new_certificate():
    cert_form = CertificateForm()
    if request.method == "POST":
        if cert_form.validate_on_submit():

            new_cert = Certificate(cn=cert_form.CN.data, san=cert_form.SAN.data)
            db.session.add(new_cert)
            db.session.commit()

            flash("certificate created", category="success")
        else:
            flash("something is wrong")
        return redirect(url_for(".certificates"))
    else:
        return render_template("new_certificate.html", form=cert_form)