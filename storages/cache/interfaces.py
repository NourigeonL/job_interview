import abc

class ICacheStorage(abc.ABC):
    
    @abc.abstractmethod
    async def get(self, input : str) -> str|None:...
    
    @abc.abstractmethod
    async def store(self, input : str, output : str) -> None:...