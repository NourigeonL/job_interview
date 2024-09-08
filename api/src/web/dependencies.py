from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from .auth_token_handler import get_current_user_from_token, UserToken
from typing import Annotated
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from api.src.features.authentication.repository import AuthenticationRepository
from api.src.features.authentication.service import AuthenticationService
from api.src.features.authentication.password_manager import PasswordManager
from api.src.features.request.service import RequestService
from api.src.features.request.crud import CRUDRequest
from api.src.web.service_locator import service_locator
from storages.cache.redis import RedisCacheStorage
import redis.asyncio as redis
from message_brokers.interfaces import IMessageBroker
from message_brokers.redis import RedisMessageBroker
from storages.db.repositories import RequestRepository
from common.config import settings
from common.exceptions import GenericError, ServiceDoesNotExistError


async def exception_handler(request: Request, e : GenericError):
    if isinstance(e, ServiceDoesNotExistError):
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"error_code": e.code, "error":e.message})
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error_code": e.code, "error":e.message})

async def get_current_user(user_token : Annotated[UserToken, Depends(get_current_user_from_token)]) -> UserToken:
    return user_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis_engine = await redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True)
        msg_broker = RedisMessageBroker(redis_engine)
        cache = RedisCacheStorage(redis_engine, settings.CACHE_DURATION_MINUTES)
        engine = create_async_engine(f"postgresql+asyncpg://{settings.POSTGRESSQL_USER}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOST}/{settings.POSTGRESQL_DB}", echo=True)
        auth_repo = AuthenticationRepository(engine)
        service_locator.set_authentication_service(AuthenticationService(auth_repo, PasswordManager()))
        request_repo = RequestRepository(engine)
        service_locator.set_request_service(RequestService(request_repo, msg_broker, cache))
        service_locator.set_crud_request(CRUDRequest(engine))
        yield
    finally:
        await engine.dispose()