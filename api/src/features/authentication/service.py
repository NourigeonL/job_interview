from api.src.features.authentication.interfaces import UserRegistrationForm, UserDto, IAuthenticationService, IAuthenticationRepository, IPasswordManager, LoginForm
from common import exceptions as ex

class AuthenticationService(IAuthenticationService):
    
    def __init__(self, repo : IAuthenticationRepository, pwd_manager : IPasswordManager) -> None:
        self.repo = repo
        self.pwd_manager = pwd_manager
    
    async def log_in_user(self, login_form : LoginForm) -> UserDto:
        user = await self.repo.get_user_by_username(login_form.username)
        if not user or not self.pwd_manager.verify_password(login_form.password, user.hashed_password):
            raise ex.InvalidCredentialsError()
        return user
    
    async def register_user(self, user_registration: UserRegistrationForm) -> UserDto:
        if await self.repo.get_user_by_username(user_registration.username):
            raise ex.InvalidCredentialsError("This username is already taken")
        user = UserDto(username=user_registration.username, hashed_password=self.pwd_manager.hash_password(user_registration.plain_password))
        return await self.repo.create_user(user)