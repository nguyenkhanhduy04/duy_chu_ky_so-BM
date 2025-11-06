"""Tạo cặp chứng chỉ dạng CA gốc tự ký và chứng chỉ ký tài liệu (end-entity).

Sinh ra:
 - ca_cert.pem (Root CA, self-signed, cA=True)
 - ca_cert.cer (DER của Root CA)
 - private_key.pem (khóa ký tài liệu, PKCS#8)
 - public_key.pem (public của chứng chỉ ký)
 - cert.pem (chứng chỉ ký – end-entity, ký bởi Root CA)
 - cert.cer (DER của chứng chỉ ký)
 - cert.pfx (PKCS#12: private key + end-entity cert + CA chain, pass 1234)
"""

import os
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12

PFX_PASSWORD = b"1234"


def tao_khoa_va_chung_chi():
    # 1) Tạo CA gốc (self-signed, cA=True)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_pub = ca_key.public_key()
    ca_name = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DUY Test Root CA"),
        x509.NameAttribute(NameOID.COMMON_NAME, "DUY Test Root CA"),
    ])
    nb = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    na = nb + datetime.timedelta(days=3650)
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_name)
        .issuer_name(ca_name)
        .public_key(ca_pub)
        .serial_number(x509.random_serial_number())
        .not_valid_before(nb)
        .not_valid_after(na)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(
            digital_signature=False,
            content_commitment=False,
            key_encipherment=False,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=True,
            crl_sign=True,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(ca_pub), critical=False)
    ).sign(private_key=ca_key, algorithm=hashes.SHA256())

    # Ghi CA
    with open("ca_cert.pem", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
    with open("ca_cert.cer", "wb") as f:
        f.write(ca_cert.public_bytes(serialization.Encoding.DER))

    # 2) Tạo khóa và chứng chỉ ký tài liệu (end-entity) ký bởi CA
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "VN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Thai Nguyen"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Thai Nguyen"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Bai Tap Chu Ky So"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Nguyen Khanh Duy Test Cert"),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, "example@example.com"),
    ])

    nb2 = datetime.datetime.utcnow() - datetime.timedelta(days=1)
    na2 = nb2 + datetime.timedelta(days=730)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_name)
        .public_key(public_key)
        .serial_number(x509.random_serial_number())
        .not_valid_before(nb2)
        .not_valid_after(na2)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_pub), critical=False)
        .add_extension(x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ), critical=True)
        .add_extension(x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.CODE_SIGNING,
            ExtendedKeyUsageOID.EMAIL_PROTECTION,
        ]), critical=False)
    ).sign(private_key=ca_key, algorithm=hashes.SHA256())

    with open("private_key.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )

    with open("public_key.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    with open("cert.cer", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.DER))

    # Include CA chain in PFX so trình kiểm tra có thể lấy ra làm trust root
    pfx_bytes = pkcs12.serialize_key_and_certificates(
        name=b"Duy Test Cert",
        key=private_key,
        cert=cert,
        cas=[ca_cert],
        encryption_algorithm=serialization.BestAvailableEncryption(PFX_PASSWORD),
    )
    with open("cert.pfx", "wb") as f:
        f.write(pfx_bytes)

    print("Đã tạo/ghi các file:")
    for fn in ["ca_cert.pem", "private_key.pem", "public_key.pem", "cert.pem", "cert.cer", "cert.pfx"]:
        print(f" - {fn} ({os.path.getsize(fn)} bytes)")


if __name__ == "__main__":
    tao_khoa_va_chung_chi()
    print("Hoàn tất tạo khóa & chứng chỉ end-entity (cA=False).")
