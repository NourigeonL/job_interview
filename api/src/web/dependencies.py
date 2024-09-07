from fastapi import Depends, FastAPI
from .auth_token_handler import get_current_user_from_token, UserToken
from typing import Annotated
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from api.src.features.authentication.repository import AuthenticationRepository
from api.src.features.authentication.service import AuthenticationService
from api.src.features.authentication.password_manager import PasswordManager
from api.src.features.process.repository import RequestRepository
from api.src.features.process.service import ProcessService
from api.src.web.service_locator import service_locator
from api.src.storages.cache.redis import RedisCacheStorage
import redis.asyncio as redis
from common.message_brokers.redis import RedisMessageBroker
from common.config import settings
async def get_current_user(user_token : Annotated[UserToken, Depends(get_current_user_from_token)]) -> UserToken:
    return user_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_engine = await redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True)
    msg_broker = RedisMessageBroker(redis_engine)
    cache = RedisCacheStorage(redis_engine, settings.CACHE_DURATION_MINUTES)
    engine = create_async_engine(f"postgresql+asyncpg://{settings.POSTGRESSQL_USER}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOST}/{settings.POSTGRESSQL_DB}", echo=True)
    auth_repo = AuthenticationRepository(engine)
    service_locator.set_authentication_service(AuthenticationService(auth_repo, PasswordManager()))
    request_repo = RequestRepository(engine)
    service_locator.set_process_service(ProcessService(request_repo, msg_broker, cache))
    
    yield
    
    await engine.dispose()