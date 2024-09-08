from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from common.storages.db.models import Request, Job
from sqlmodel import select, and_, update
from common.message_brokers.interfaces import ResponseDict, RequestDict
from common.enums import RequestStatus
from uuid import UUID

class RequestRepository:
    
    def __init__(self, engine : AsyncEngine) -> None:
        self.engine = engine
        self.async_session = async_sessionmaker(engine)
        
    async def create_job(self, user_id : UUID) -> Job:
        async with self.async_session() as session:
            job = Job(user_id=user_id)
            session.add(job)
            await session.commit()
            await session.refresh(job)
        return job
    
    async def update_requests_status(self, requests : list[RequestDict], status : RequestStatus) -> None:
        async with self.async_session() as session:
            for request in requests:
                stmt = update(Request).where(Request.id == request['request_id']).values(status=status.value)
                await session.execute(stmt)
            await session.commit()
    
    async def set_requests_to_fail(self, failed_requests : list[RequestDict]) -> None:
        async with self.async_session() as session:
            for request in failed_requests:
                stmt = update(Request).where(Request.id == request['request_id']).values(status=RequestStatus.FAILED)
                await session.execute(stmt)
            await session.commit()
        
    async def create_request(self, request: RequestDict) -> RequestDict:
        async with self.async_session() as session:
            db_request = Request(job_id=request['job_id'], user_id=request['user_id'], input=request['input'], status=RequestStatus.PENDING.value)
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
                    db_request = Request(job_id=response['job_id'], user_id=response['user_id'], input=response['input'], output=response['output'], status=RequestStatus.COMPLETED)
                else:
                    stmt = select(Request).where(Request.id ==request_id)
                    result = await session.execute(stmt)
                    db_request = result.scalar_one()
                    db_request.status = RequestStatus.COMPLETED
                    db_request.output = response['output']
                session.add(db_request)
            await session.commit()