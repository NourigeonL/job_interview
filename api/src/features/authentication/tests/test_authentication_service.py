import unittest
import pytest
from api.src.features.authentication.interfaces import User, IAuthenticationRepository, IPasswordManager, UserRegistrationForm, LoginForm
from api.src.features.authentication.service import AuthenticationService
from common import exceptions as ex
from uuid import uuid4

class FakeAuthenticationRepository(IAuthenticationRepository):
    def __init__(self) -> None:
        self.db : list[User] = []
    
    async def get_user_by_username(self, username: str) -> User | None:
        for user in self.db:
            if user.username == username:
                return user
        return None
    
    async def create_user(self, user : User) -> User:
        if user.id is None:
            user.id = uuid4()
            self.db.append(user)
        else:
            for db_user in self.db:
                if db_user.id == user.id:
                    db_user.username = user.username
                    db_user.hashed_password = user.hashed_password
        return user
        
        

class FakePasswordManager(IPasswordManager):
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return plain_password == hashed_password
    
    def hash_password(self, plain_password : str) -> str:
        return plain_password

class TestAuthenticationService(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.repo = FakeAuthenticationRepository()
        self.pwd_manager = FakePasswordManager()
        self.service = AuthenticationService(self.repo, self.pwd_manager)
        self.repo.db.append(User(id=uuid4(), username="user1", hashed_password="password"))
        
    async def test_should_raise_error_if_username_does_not_exist(self):
        with pytest.raises(ex.InvalidCredentialsError):
            await self.service.log_in_user(LoginForm(username="wrong_user_name", password="password"))
            
    async def test_should_raise_error_if_wrong_password(self):
        with pytest.raises(ex.InvalidCredentialsError):
            await self.service.log_in_user(LoginForm(username="user1", password="wrong_password"))
            
    async def test_should_return_user_if_correct_credentials(self):
        user = await self.service.log_in_user(LoginForm(username="user1", password="password"))
        assert user.id == self.repo.db[0].id
        assert user.username == self.repo.db[0].username
        
    async def test_should_register_user(self):
        plain_password = "password2"
        username = "user2"
        user = await self.service.register_user(UserRegistrationForm(username="user2", plain_password="password2"))
        assert len(self.repo.db) == 2
        assert user.username == username
        assert self.pwd_manager.verify_password(plain_password, user.hashed_password)
        
    async def test_should_raise_error_if_username_is_already_taken(self):
        with pytest.raises(ex.InvalidCredentialsError):
            await self.service.register_user(UserRegistrationForm(username="user1", plain_password="password2"))