from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from common.storages.db.models import Request, RequestRead, RequestPatch
from sqlmodel import select, and_, delete
from uuid import UUID

class CRUDRequest:
    
    def __init__(self, engine : AsyncEngine) -> None:
        self.engine = engine
        self.async_session = async_sessionmaker(engine)
        
    async def get(self, user_id : UUID, request_id: UUID) -> Request | None:
        async with self.async_session() as session:
            stmt = select(Request).where(and_(Request.user_id == user_id, Request.id == request_id))
            result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, user_id : UUID) -> list[Request]:
        async with self.async_session() as session:
            stmt = select(Request).where(Request.user_id == user_id)
            result = await session.execute(stmt)
        return result.scalars().all()
    
    async def delete(self, user_id : UUID, request_id: UUID) -> bool:
        async with self.async_session() as session:
            stmt = delete(Request).where(and_(Request.user_id == user_id, Request.id == request_id))
            await session.execute(stmt)
            await session.commit()
        return True
    
    async def patch(self, user_id : UUID, request_id: UUID, data : RequestPatch) -> Request:
        async with self.async_session() as session:
            request = await self.get(user_id, request_id)
            values = data.model_dump(exclude_unset=True)

            for k, v in values.items():
                setattr(request, k, v)
                
            session.add(request)
            await session.commit()
            await session.refresh(request)
        
        return request