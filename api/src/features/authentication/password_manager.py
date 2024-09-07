import bcrypt
from .interfaces import IPasswordManager

class PasswordManager(IPasswordManager):
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    
    def hash_password(self, plain_password : str) -> str:
        return bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt()).decode()