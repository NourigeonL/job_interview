from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from common.storages.db.models import Request
from sqlmodel import select, and_
from common.message_brokers.interfaces import ResponseDict, RequestDict
import abc
from common.enums import RequestStatus
class IRequestRepository(abc.ABC):
    
    @abc.abstractmethod
    async def save_responses(self, responses : list[ResponseDict]) -> None:...
    
    @abc.abstractmethod
    async def create_request(self, request: RequestDict) -> RequestDict:...

class RequestRepository:
    
    def __init__(self, engine : AsyncEngine) -> None:
        self.engine = engine
        self.async_session = async_sessionmaker(engine)
        
    async def create_request(self, request: RequestDict) -> RequestDict:
        async with self.async_session() as session:
            db_request = Request(user_id=request['user_id'], input=request['input'], status=RequestStatus.PENDING.value)
            session.add(db_request)
            await session.commit()
            await session.refresh(db_request)
            request['request_id'] = str(db_request.id)
        return request
        
    async def save_responses(self, responses: list[ResponseDict]) -> None:
        async with self.async_session() as session:
            for response in responses:
                request_id =  response.get("request_id")
                if not request_id:
                    db_request = Request(user_id=response['user_id'], input=response['input'], output=response['output'], status=RequestStatus.COMPLETED)
                else:
                    stmt = select(Request).where(Request.id ==request_id)
                    result = await session.execute(stmt)
                    db_request = result.scalar_one()
                    db_request.status = RequestStatus.COMPLETED
                    db_request.output = response['output']
                session.add(db_request)
            await session.commit()