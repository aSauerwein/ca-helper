import zipfile
from io import BytesIO
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from flask import flash, redirect, render_template, request, send_file, url_for

from .. import db
from ..models import Certificate
from . import main
from .crypto import create_key_pair
from .forms import CertificateForm

root_key_path = Path("cfssl-ca/rootca.key")
root_crt_path = Path("flask-app/static/rootca.pem")


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/certificates", methods=["GET"])
def certificates():

    certs = Certificate.query.all()
    data = []
    for cert in certs:
        data.append(
            {
                "ID": cert.id,
                "Subject": cert.subject,
                "Not Before": cert.not_valid_before,
                "Not After": cert.not_valid_after,
                "Issuer": cert.issuer.subject if cert.issuer else "self",
            }
        )

    return render_template("certificates.html", data=data)


@main.route("/certificates/new", methods=["GET", "POST"])
def new_certificate():
    cert_form = CertificateForm()
    choices = [(0, "self")]
    cas = Certificate.query.filter_by(ca=True).all()
    for ca in cas:
        choices.append((ca.id, ca.subject))
    cert_form.Issuer.choices = choices
    if request.method == "POST":
        if cert_form.validate_on_submit():
            options = {}
            issuer_id = int(request.form.get("Issuer"))
            if issuer_id != 0:
                # get certificate private key from database
                issuer = Certificate.query.get(issuer_id)
                options["ca_crt"] = issuer.public_key
                options["ca_key"] = issuer.private_key
            else:
                options["ca_crt"] = "self"

            options["name"] = {
                "country": request.form.get("Country", ""),
                "state_provice": request.form.get("State_Provice", ""),
                "locality": request.form.get("Locality", ""),
                "organization": request.form.get("Organization", ""),
                "common": request.form.get("Common", ""),
            }
            options["san"] = request.form.get("SAN", "").split(",")
            options["validity"] = int(request.form.get("Validity", 30))
            options["ca"] = "CA" in request.form

            key, cert = create_key_pair(**options)
            new_cert = Certificate(
                public_key=cert.public_bytes(serialization.Encoding.PEM),
                private_key=key,
                subject=str(cert.subject),
                not_valid_before=cert.not_valid_before,
                not_valid_after=cert.not_valid_after,
                ca=options.get("ca", False),
                issuer_id=issuer_id,
            )
            db.session.add(new_cert)
            # db.session.flush()
            # if issuer_id == 0:
            #     # self signed
            #     new_cert.issuer_id = new_cert.id
            db.session.commit()

            flash("certificate created", category="success")
        else:
            flash("something is wrong")
        return redirect(url_for(".certificates"))
    else:
        return render_template("new_certificate.html", form=cert_form)


@main.route("/certificates/download", methods=["GET"])
def download_certificate():
    cert_id = request.values.get("ID")
    cert = Certificate.query.get(cert_id)
    # create public and private key to download as zip
    memory_file = BytesIO()
    memory_file.seek(0)
    with zipfile.ZipFile(memory_file, "w") as zf:
        data = zipfile.ZipInfo("crt.key")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, cert.private_key)
        data = zipfile.ZipInfo("crt.pem")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, cert.public_key)
    memory_file.seek(0)
    return send_file(
        memory_file,
        attachment_filename="crt.zip",
        as_attachment=True,
        cache_timeout=1,
    )
