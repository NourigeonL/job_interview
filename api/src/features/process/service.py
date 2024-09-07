from uuid import UUID
from api.src.features.process.interfaces import IProcessService, IRequestRepository, RequestForm
from common.message_brokers.interfaces import Request, IMessageBroker, Response
from api.src.storages.cache.interfaces import ICacheStorage
class ProcessService(IProcessService):
    
    def __init__(self, repo : IRequestRepository, msg_broker : IMessageBroker, cache : ICacheStorage) -> None:
        self.repo = repo
        self.msg_broker = msg_broker
        self.cache = cache
    
    async def process_requests(self, user_id: UUID, request_form : RequestForm) -> None:
        need_to_process_requests : list[Request] = []
        cached_responses : list[Response]= []
        for request in request_form.requests:
            response = await self.cache.get(request)
            if response:
                cached_responses.append({"user_id":str(user_id), "input":request, "output": response})
            else:
                need_to_process_requests.append({"user_id": user_id, "input": request})
        if len(cached_responses) > 0:
            await self.repo.save_responses(cached_responses)
        nb_requests = len(need_to_process_requests)
        await self.msg_broker.send_requests(need_to_process_requests)
        nb_reponses = 0
        while nb_reponses < nb_requests:
            responses = await self.msg_broker.receive_reponses(nb_requests)
            if len(responses) > 0:
                nb_reponses += len(responses)
                await self.repo.save_responses(responses)
                for response in responses:
                    await self.cache.store(response["input"], response["output"])
        