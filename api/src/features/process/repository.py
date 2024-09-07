from uuid import UUID
from api.src.features.process.interfaces import IRequestRepository
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from api.src.storages.db import models
from sqlmodel import select

from common.message_brokers.interfaces import Response

class RequestRepository(IRequestRepository):
    
    def __init__(self, engine : AsyncEngine) -> None:
        self.engine = engine
        self.async_session = async_sessionmaker(engine)
        
    async def save_responses(self, responses: list[Response]) -> None:
        async with self.async_session() as session:
            for response in responses:
                session.add(models.Request(user_id=response['user_id'], input=response['input'], output=response['output']))
            await session.commit()