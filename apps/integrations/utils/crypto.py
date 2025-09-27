from cryptography.fernet import Fernet
from django.conf import settings

class TokenEncryptor:
    """
    class For token encryption
    """
    fernet = Fernet(settings.ENCRYPTION_KEY.encode())

    @staticmethod
    def encrypt(data: str) -> str:
        return TokenEncryptor.fernet.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt(token: str) -> str:
        return TokenEncryptor.fernet.decrypt(token.encode()).decode()