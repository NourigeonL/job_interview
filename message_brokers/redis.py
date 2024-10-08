from redis.asyncio import Redis
from message_brokers.interfaces import IMessageBroker, RequestDict, ResponseDict
import json
class RedisMessageBroker(IMessageBroker):

    def __init__(self, redis : Redis) -> None:
        self.db = redis
        self.input_queue = "input_queue"
        self.output_queue = "output_queue"
        
    async def receive_requests(self, batch_size: int) -> list[RequestDict]:
        new_requests = await self.db.rpop(self.input_queue, batch_size)
        if not new_requests:
            return []
        return [json.loads(r) for r in new_requests]
    
    async def receive_reponses(self, batch_size: int) -> list[ResponseDict]:
        new_responses = await self.db.rpop(self.output_queue, batch_size)
        if not new_responses:
            return []
        return [json.loads(r) for r in new_responses]
    
    async def send_requests(self, requests: list[RequestDict]) -> None:
        await self.db.lpush(self.input_queue, *[json.dumps(r) for r in requests])
    
    async def send_responses(self, responses: list[ResponseDict]) -> None:
        await self.db.lpush(self.output_queue,*[json.dumps(response) for response in responses])