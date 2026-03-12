from __future__ import annotations

import base64
import secrets
from typing import TYPE_CHECKING

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from tornado.web import HTTPError

if TYPE_CHECKING:
    from .handlers import BaseHandler


def generate_keypair() -> tuple[rsa.RSAPublicKey, rsa.RSAPrivateKey, str]:
    user_secret = secrets.token_urlsafe(16)
    # user_secret = "something"
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend(),
    )
    public_key = private_key.public_key()

    return public_key, private_key, user_secret


def create_private_pem(private_key: rsa.RSAPrivateKey, user_secret: str):
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            user_secret.encode()
        ),
    )


def load_from_pem(
    private_pem: bytes, user_secret: str
) -> tuple[rsa.RSAPublicKey, rsa.RSAPrivateKey]:
    private_key = load_pem_private_key(
        private_pem, user_secret.encode(), default_backend()
    )
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise HTTPError(401, "Not an RSA key")

    public_key = private_key.public_key()

    return public_key, private_key


def get_signed_cookie(
    private_pem: bytes, user_secret: str, user_name: str = "local"
) -> str:
    _, private_key = load_from_pem(private_pem, user_secret)
    signature = private_key.sign(
        data=user_secret.encode("utf-8"),
        padding=padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        algorithm=hashes.SHA256(),
    )

    return f"{user_name}|{base64.b64encode(signature).decode()}"


def authenticate(self: BaseHandler) -> str:
    cookie_data = self.get_cookie(self.application.cookie_name)
    if cookie_data is None:
        raise HTTPError(401, "No cookie provided")

    try:
        public_key, _ = load_from_pem(
            self.application.private_pem,
            self.application.cookie_secret,
        )

        # Split the user and signature out
        user, sig64 = f"{cookie_data}=".split("|", 1)

        # Skip verification in developer mode
        if self.application.developer_mode:
            return user

        public_key.verify(
            signature=base64.b64decode(sig64),
            data=self.application.cookie_secret.encode("utf-8"),
            padding=padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            algorithm=hashes.SHA256(),
        )
    except InvalidSignature as exc:
        raise HTTPError(403, "Invalid key signature") from exc

    return user
