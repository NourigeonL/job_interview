from api.src.features.authentication.interfaces import IAuthenticationRepository, User
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from common.storages.db import models
from sqlmodel import select

class AuthenticationRepository(IAuthenticationRepository):
    
    def __init__(self, engine : AsyncEngine) -> None:
        self.engine = engine
        self.async_session = async_sessionmaker(engine)
        
    async def create_user(self, user: User) -> User:
        async with self.async_session() as session:
            db_user = models.User(username=user.username, hashed_password=user.hashed_password)
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
        user.id = db_user.id
        return user
    
    async def get_user_by_username(self, username: str) -> User | None:
        async with self.async_session() as session:
            stmt = select(models.User).where(models.User.username == username)
            result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            return None
        return User(id=user.id, username=user.username, hashed_password=user.hashed_password)