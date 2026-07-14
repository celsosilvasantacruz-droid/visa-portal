from cryptography.fernet import Fernet
from django.conf import settings

cipher_suite = Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    if not data: return ""
    return "ENC:" + cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data or not encrypted_data.startswith("ENC:"):
        return encrypted_data
    return cipher_suite.decrypt(encrypted_data[4:].encode()).decode()
