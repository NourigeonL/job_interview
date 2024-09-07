import abc
from common.message_brokers.interfaces import IMessageBroker, Request, Response
from uuid import UUID
from pydantic import BaseModel

class RequestForm(BaseModel):
    requests : list[str]

class IRequestRepository(abc.ABC):
    
    @abc.abstractmethod
    async def save_responses(self, responses : list[Response]) -> None:...

class IProcessService(abc.ABC):
    
    @abc.abstractmethod
    async def process_requests(self, user_id : UUID, request_form : RequestForm) -> None:...