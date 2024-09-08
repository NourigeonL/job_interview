from uuid import UUID
from common.message_brokers.interfaces import RequestDict, IMessageBroker, ResponseDict
from common.storages.cache.interfaces import ICacheStorage
from common.storages.db.repositories import RequestRepository
import time
class ProcessService:
    
    def __init__(self, repo : RequestRepository, msg_broker : IMessageBroker, cache : ICacheStorage) -> None:
        self.repo = repo
        self.msg_broker = msg_broker
        self.cache = cache
        self.stop = False
    
    async def send_requests(self, user_id: UUID, requests : list[str]) -> UUID:
        need_to_process_requests : list[RequestDict] = []
        cached_responses : list[ResponseDict]= []
        new_job = await self.repo.create_job(user_id)
        for request in requests:
            request_dict = {"job_id": str(new_job.id),"user_id":str(user_id), "input":request}
            response = await self.cache.get(request)
            if response:
                request_dict["output"] = response
                cached_responses.append(request_dict)
            else:
                request = await self.repo.create_request(request_dict)
                need_to_process_requests.append(request)
        if len(cached_responses) > 0:
            await self.repo.save_responses(cached_responses)
        await self.msg_broker.send_requests(need_to_process_requests)
        return new_job.id
            
        