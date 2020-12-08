from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime
import re
import ipaddress


def create_key(key_size=2048):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    return key


def create_csr(key, **kwargs):
    csr = x509.CertificateSigningRequestBuilder().subject_name(
        x509.Name(
            [
                # Provide various details about who we are.
                x509.NameAttribute(NameOID.COUNTRY_NAME, kwargs["name"].get("country")),
                x509.NameAttribute(
                    NameOID.STATE_OR_PROVINCE_NAME, kwargs["name"].get("state_provice")
                ),
                x509.NameAttribute(NameOID.LOCALITY_NAME, kwargs["name"].get("locality")),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, kwargs["name"].get("organization")),
                x509.NameAttribute(NameOID.COMMON_NAME, kwargs["name"].get("common")),
            ]
        )
    )
    # build list of sans
    # valid types:
    # x509.DNSName
    # x509.IPAddress
    # x509.RFC822Name - email
    san = []
    for entry in kwargs.get("san"):
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", entry):
            # ipv4 address
            san.append(x509.IPAddress(ipaddress.IPv4Address(entry)))
        elif re.match(r"^[A-Za-z0-9-\.]{1,63}", entry):
            # dns
            san.append(x509.DNSName(entry))
        elif re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", entry):
            # email
            san.append(x509.RFC822Name(entry))
        else:
            print(f"{entry} not valid for SAN")

    # only add extension if san is not empty
    if san:
        csr = csr.add_extension(
            x509.SubjectAlternativeName(san),
            critical=False,
            # Sign the CSR with our private key.
        )

    csr = csr.sign(key, hashes.SHA256())
    return csr


def sign_csr(csr, **kwargs):
    if kwargs.get("ca_crt") == "self":
        issuer_subject = csr.subject
        ca_key = kwargs.get("ca_key")
    else:
        # load private/public key from pem
        ca_key = serialization.load_pem_private_key(kwargs.get("ca_key"), None)
        ca_crt = x509.load_pem_x509_certificate(kwargs.get("ca_crt"))
        issuer_subject = ca_crt.subject

    # set ca constraint to true/false
    bc = (x509.BasicConstraints(ca=kwargs.get("ca"), path_length=None), True)

    valdity = kwargs.get("validity", 30)
    valid_from = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    valid_to = datetime.datetime.utcnow() + datetime.timedelta(days=valdity)

    builder = x509.CertificateBuilder(
        issuer_name=issuer_subject,
        subject_name=csr.subject,
        public_key=csr.public_key(),
        not_valid_before=valid_from,
        not_valid_after=valid_to,
        serial_number=x509.random_serial_number(),
    )

    builder = builder.add_extension(*bc)
    builder = builder.add_extension(
        x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]), critical=True
    )

    for e in csr.extensions:
        builder = builder.add_extension(e.value, e.critical)

    return builder.sign(ca_key, hashes.SHA256())


def create_key_pair(**kwargs):
    key = create_key()
    csr = create_csr(key, **kwargs)

    if "ca_key" not in kwargs:
        kwargs["ca_key"] = key

    cert = sign_csr(csr, **kwargs)

    key_string = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return key_string, cert
