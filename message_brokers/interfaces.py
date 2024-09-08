import abc
from typing import TypedDict, TypeVar

T = TypeVar("T")

class MessageDict(TypedDict):
    name : str
    data : dict


class IMessage(abc.ABC):
    
    @abc.abstractmethod
    def to_dict(self) -> MessageDict:...
    
    @classmethod
    def from_dict(cls : type[T], data : dict) -> T:
        return cls(**data)

class RequestDict(TypedDict):
    job_id : str
    request_id : str
    user_id : str
    input : str
    status : str

class ResponseDict(RequestDict):
    output : str


class IMessageBroker(abc.ABC):
    
    @abc.abstractmethod
    async def send_requests(self, requests : list[RequestDict]) -> None:...
    
    @abc.abstractmethod
    async def receive_requests(self, batch_size : int) -> list[RequestDict]:...
    
    @abc.abstractmethod
    async def send_responses(self, reponses : list[ResponseDict]) -> None:...
    
    @abc.abstractmethod
    async def receive_reponses(self, batch_size : int) -> list[ResponseDict]:...
    
    