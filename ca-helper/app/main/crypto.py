from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime


def create_key(key_size=2048):
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    return key


def create_csr(key, **kwargs):
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    # Provide various details about who we are.
                    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
                    x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
                ]
            )
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    # Describe what sites we want this certificate for.
                    x509.DNSName(u"mysite.com"),
                    x509.DNSName(u"www.mysite.com"),
                    x509.DNSName(u"subdomain.mysite.com"),
                ]
            ),
            critical=False,
            # Sign the CSR with our private key.
        )
        .sign(key, hashes.SHA256())
    )
    return csr


def sign_csr(csr, ca_key, ca_crt="", **kwargs):
    if ca_crt == "":
        # self signed root ca
        issuer_subject = csr.subject
        bc = (x509.BasicConstraints(ca=True, path_length=None), True)

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
    cert = sign_csr(csr, key, **kwargs)

    key_string = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return key_string, cert