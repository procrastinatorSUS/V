import base64
import hashlib

from cryptography.fernet import Fernet


def build_cipher(secret: str) -> Fernet:
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(cipher: Fernet, value: str) -> str:
    return cipher.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(cipher: Fernet, value: str) -> str:
    return cipher.decrypt(value.encode("utf-8")).decode("utf-8")
