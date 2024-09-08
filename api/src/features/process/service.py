from uuid import UUID
from api.src.features.process.interfaces import IProcessService
from common.message_brokers.interfaces import RequestDict, IMessageBroker, ResponseDict
from common.storages.cache.interfaces import ICacheStorage
from common.storages.db.repositories import IRequestRepository
import time
class ProcessService(IProcessService):
    
    def __init__(self, repo : IRequestRepository, msg_broker : IMessageBroker, cache : ICacheStorage) -> None:
        self.repo = repo
        self.msg_broker = msg_broker
        self.cache = cache
        self.stop = False
    
    def stop_sub_process(self) -> None:
        self.stop = True
    
    async def process_requests(self, user_id: UUID, requests : list[str]) -> None:
        need_to_process_requests : list[RequestDict] = []
        cached_responses : list[ResponseDict]= []
        for request in requests:
            response = await self.cache.get(request)
            if response:
                cached_responses.append({"user_id":str(user_id), "input":request, "output": response})
            else:
                request = await self.repo.create_request({"user_id":str(user_id), "input":request})
                need_to_process_requests.append(request)
        if len(cached_responses) > 0:
            await self.repo.save_responses(cached_responses)
        await self.msg_broker.send_requests(need_to_process_requests)
            
        