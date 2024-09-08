import abc
from uuid import UUID

class IProcessService(abc.ABC):
    
    @abc.abstractmethod
    async def process_requests(self, user_id : UUID, requests : list[str]) -> None:...
    
    @abc.abstractmethod
    def stop_sub_process(self) -> None:...