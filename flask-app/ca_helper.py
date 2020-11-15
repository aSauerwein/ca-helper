import json
import zipfile
from io import BytesIO
from pathlib import Path
from subprocess import PIPE, run

from flask import Flask, render_template, request, send_file
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_pyfile("config.py")
Bootstrap(app)

root_key_path = Path("cfssl-ca/rootca.key")
root_crt_path = Path("flask-app/static/rootca.pem")


@app.route("/")
def hello():
    return render_template("index.html", rootca=root_crt_path.is_file())


@app.route("/init-ca")
def init_ca():
    # create cfssl ca directory
    ca_folder = Path("cfssl-ca")
    ca_folder.mkdir(exist_ok=True)

    csr = app.config["ROOT"]
    output = run(
        ["cfssl", "genkey", "-initca", "-"],
        stdout=PIPE,
        input=json.dumps(csr),
        encoding="ascii",
    )
    message = ""
    if output.returncode == 0:
        output_dict = json.loads(output.stdout)
        # write ca crt
        root_crt_path.write_text(output_dict["cert"])
        # write ca key
        root_key_path.write_text(output_dict["key"])
        message = "successfully created root ca cert + key"
    else:
        message = "creation failed"

    return {
        "message": message,
        "returncode": output.returncode,
    }


@app.route("/create-cert", methods=["POST"])
def create_cert():
    csr = app.config["LEAF"]
    csr["hosts"] = request.form.get("SAN").split(",")
    csr["CN"] = request.form.get("CN")
    csr_output = run(
        [
            "cfssl",
            "genkey",
            "-",
        ],
        stdout=PIPE,
        input=json.dumps(csr),
        encoding="ascii",
    )
    if csr_output.returncode != 0:
        return {
            "message": "could not create csr/key",
            "returncode": csr_output.returncode,
        }

    csr_dict = json.loads(csr_output.stdout)
    crt_output = run(
        [
            "cfssl",
            "sign",
            "-ca",
            root_crt_path,
            "-ca-key",
            root_key_path,
            "-",
        ],
        stdout=PIPE,
        input=csr_dict["csr"],
        encoding="ascii",
    )
    if crt_output.returncode != 0:
        return {
            "message": "could not create crt",
            "returncode": crt_output.returncode,
        }

    crt_dict = json.loads(crt_output.stdout)
    memory_file = BytesIO()
    memory_file.seek(0)
    with zipfile.ZipFile(memory_file, "w") as zf:
        data = zipfile.ZipInfo("crt.key")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, csr_dict["key"])
        data = zipfile.ZipInfo("crt.pem")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, crt_dict["cert"])
        data = zipfile.ZipInfo("crt.csr")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, csr_dict["csr"])
    memory_file.seek(0)
    return send_file(
        memory_file,
        attachment_filename="crt.zip",
        as_attachment=True,
        cache_timeout=1,
    )


@app.route("/upload-csr", methods=["POST"])
def upload_csr():
    file = request.files["file"]
    csr = file.stream.read().decode()
    crt_output = run(
        [
            "cfssl",
            "sign",
            "-ca",
            root_crt_path,
            "-ca-key",
            root_key_path,
            "-",
        ],
        stdout=PIPE,
        input=csr,
        encoding="ascii",
    )
    if crt_output.returncode != 0:
        return {
            "message": "could not create crt",
            "returncode": crt_output.returncode,
        }
    crt_dict = json.loads(crt_output.stdout)
    memory_file = BytesIO()
    memory_file.seek(0)
    with zipfile.ZipFile(memory_file, "w") as zf:
        data = zipfile.ZipInfo("crt.pem")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, crt_dict["cert"])
        data = zipfile.ZipInfo("crt.csr")
        data.compress_type = zipfile.ZIP_DEFLATED
        zf.writestr(data, csr)
    memory_file.seek(0)
    return send_file(
        memory_file,
        attachment_filename="crt.zip",
        as_attachment=True,
        cache_timeout=1,
    )