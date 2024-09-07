import abc
from pydantic import BaseModel
from uuid import UUID

class User(BaseModel):
    id : UUID | None = None
    username : str
    hashed_password : str
    
class UserRegistrationForm(BaseModel):
    username : str
    plain_password : str

class LoginForm(BaseModel):
    username : str
    password : str

class IAuthenticationRepository(abc.ABC):
    
    @abc.abstractmethod
    async def get_user_by_username(self, username : str) -> User | None:...
    
    @abc.abstractmethod
    async def create_user(self, user : User) -> User:...

class IAuthenticationService(abc.ABC):
    
    @abc.abstractmethod
    async def log_in_user(self, login_form : LoginForm) -> User:...
    
    @abc.abstractmethod
    async def register_user(self, user_registration : UserRegistrationForm) -> User:...
    
class IPasswordManager(abc.ABC):
    
    @abc.abstractmethod
    def verify_password(self, plain_password : str, hashed_password : str) -> bool:...
    
    @abc.abstractmethod
    def hash_password(self, plain_password : str) -> str:...