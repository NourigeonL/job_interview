from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from storages.db.models import Request, RequestPatch, Job
from sqlmodel import select, and_, delete, desc
from uuid import UUID
from common.enums import RequestStatus
from datetime import datetime
from sqlalchemy.orm import joinedload
from pydantic import BaseModel

class RequestInfoDto(BaseModel):
    request_id : UUID
    input : str
    output : str | None
    status : RequestStatus
    created_at : datetime
    last_update : datetime
    

class JobSummary(BaseModel):
    job_id : UUID
    created_at : datetime
    nb_requests : int
    last_update : datetime
    status : str

class JobInfoDto(JobSummary):
    requests : list[RequestInfoDto]


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
            stmt = select(Request).where(Request.user_id == user_id).order_by(desc(Request.created_at))
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
    
    def __get_job_status(self, lst_status : list[RequestStatus]) -> str:
        nb_completed = lst_status.count(RequestStatus.COMPLETED)
        nb_pending = lst_status.count(RequestStatus.PENDING)
        nb_in_process = lst_status.count(RequestStatus.IN_PROCESS)
        nb_failed = lst_status.count(RequestStatus.FAILED)
        nb_requests = len(lst_status)
        
        status = ""
        if nb_completed > 0:
            status += f"{nb_completed}({100*nb_completed//nb_requests}%) requests completed"
        if nb_in_process > 0:
            status += f", {nb_in_process}({100*nb_in_process//nb_requests}%) requests in process"
        if nb_pending > 0:
            status += f"{nb_pending}({100*nb_pending//nb_requests}%) requests pending"
        if nb_failed > 0:
            status += f"{nb_failed}({100*nb_failed//nb_requests}%) requests failed"
        return status
    
    async def get_jobs_summary(self, user_id : UUID) -> list[JobSummary]:
        async with self.async_session() as session:
            stmt = select(Job).where(Job.user_id == user_id).options(joinedload(Job.requests)).order_by(desc(Job.created_at))
            result = await session.scalars(stmt)
            jobs = result.unique().all()
            lst_job_summary = []
            for job in jobs:
                last_update = job.updated_at
                lst_status = []
                for request in job.requests:
                    lst_status.append(request.status)
                    if request.updated_at > last_update:
                        last_update = request.updated_at
                lst_job_summary.append(JobSummary(job_id=job.id, nb_requests=len(job.requests), created_at=job.created_at, last_update=last_update, status=self.__get_job_status(lst_status)))
        return lst_job_summary
        
    
    async def get_job_info(self, user_id : UUID, job_id : UUID) -> JobInfoDto| None:
        async with self.async_session() as session:
            stmt = select(Job).where(and_(Job.id == job_id, Job.user_id == user_id)).options(joinedload(Job.requests))
            result = await session.scalars(stmt)
            job = result.unique().one_or_none()
            if not job:
                return None
            requests = []
            last_update = job.updated_at
            lst_status = []
            for request in job.requests:
                lst_status.append(request.status)
                if request.updated_at > last_update:
                    last_update = request.updated_at
                requests.append(RequestInfoDto(request_id=request.id, input=request.input, output=request.output, status=request.status, created_at=request.created_at, last_update=request.updated_at))
            return JobInfoDto(job_id=job.id, nb_requests=len(requests), created_at=job.created_at, requests=requests, last_update=last_update, status=self.__get_job_status(lst_status))
            