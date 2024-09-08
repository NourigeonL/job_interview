import abc
from pydantic import BaseModel
from uuid import UUID

class UserDto(BaseModel):
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
    async def get_user_by_username(self, username : str) -> UserDto | None:...
    
    @abc.abstractmethod
    async def create_user(self, user : UserDto) -> UserDto:...

class IAuthenticationService(abc.ABC):
    
    @abc.abstractmethod
    async def log_in_user(self, login_form : LoginForm) -> UserDto:...
    
    @abc.abstractmethod
    async def register_user(self, user_registration : UserRegistrationForm) -> UserDto:...
    
class IPasswordManager(abc.ABC):
    
    @abc.abstractmethod
    def verify_password(self, plain_password : str, hashed_password : str) -> bool:...
    
    @abc.abstractmethod
    def hash_password(self, plain_password : str) -> str:...