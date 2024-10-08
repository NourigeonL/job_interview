from uuid import UUID
from message_brokers.interfaces import RequestDict, IMessageBroker, ResponseDict
from storages.cache.interfaces import ICacheStorage
from storages.db.repositories import RequestRepository

class RequestService:
    
    def __init__(self, repo : RequestRepository, msg_broker : IMessageBroker, cache : ICacheStorage) -> None:
        self.repo = repo
        self.msg_broker = msg_broker
        self.cache = cache
    
    async def send_requests(self, user_id: UUID, requests : list[str]) -> UUID:
        """If a request is cached, save the response in the db directly, else send to the AI for processing

        Args:
            user_id (UUID): The user id
            requests (list[str]): The list of input to process

        Returns:
            UUID: job id
        """
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
        if len(need_to_process_requests) > 0:
            await self.msg_broker.send_requests(need_to_process_requests)
        return new_job.id
            
        