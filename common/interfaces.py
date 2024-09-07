import abc
from typing import TypedDict, TypeVar


class MessageDict(TypedDict):
    name : str
    data : dict


class IMessage(abc.ABC):
    
    @abc.abstractmethod
    def to_dict(self) -> MessageDict:...


class IMessageBroker(abc.ABC):
    
    @abc.abstractmethod
    async def send(self) -> None:...