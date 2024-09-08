from api.src.features.authentication.interfaces import IAuthenticationRepository, UserDto
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from storages.db.models import User
from sqlmodel import select

class AuthenticationRepository(IAuthenticationRepository):
    
    def __init__(self, engine : AsyncEngine) -> None:
        self.engine = engine
        self.async_session = async_sessionmaker(engine)
        
    async def create_user(self, user: UserDto) -> UserDto:
        async with self.async_session() as session:
            db_user = User(username=user.username, hashed_password=user.hashed_password)
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
        user.id = db_user.id
        return user
    
    async def get_user_by_username(self, username: str) -> UserDto | None:
        async with self.async_session() as session:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        return UserDto(id=user.id, username=user.username, hashed_password=user.hashed_password)