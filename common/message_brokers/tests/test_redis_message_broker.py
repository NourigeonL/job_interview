import unittest
import redis.asyncio as redis
from common.message_brokers.redis import RedisMessageBroker
from common.message_brokers.interfaces import Request
import asyncio
import json
class TestRedisPubSub(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.r = await redis.from_url("redis://localhost/1", encoding="utf-8", decode_responses=True)
        await self.r.flushdb()
        
    async def test_should_publish(self):
        
        async def reader(channel: redis.client.PubSub):
            while True:
                message = await channel.get_message(ignore_subscribe_messages=True, timeout=None)
                if message is not None:
                    assert message["data"] == {"input" : "Hello"}
                    break
            
        
        async with self.r.pubsub() as pubsub:
            await pubsub.subscribe("channel:1")
            future = asyncio.create_task(reader(pubsub))
            await self.r.publish("channel:1", {"input" : "Hello"})
            await future
            
    async def test_should_push(self):
        request1 : Request = {"input" : "some value"}
        request2 : Request = {"input" : "other value"}
        await self.r.lpush("input", json.dumps(request1), json.dumps(request2))
        new_requests = await self.r.rpop("input", 10)
        print(new_requests)
        assert len(new_requests) == 2, new_requests
        assert json.loads(new_requests[0]) == request1
        assert json.loads(new_requests[1]) == request2
        
    async def test_should_not_pop_again(self):
        request1 : Request = {"input" : "some value"}
        request2 : Request = {"input" : "other value"}
        await self.r.lpush("input", *[json.dumps(request1), json.dumps(request2)])
        await self.r.rpop("input", 10)
        new_requests = await self.r.rpop("input", 10)
        assert new_requests is None
        
    async def test_should_return_list(self):
        request1 : Request = {"input" : "some value"}
        await self.r.lpush("input", json.dumps(request1))
        new_requests = await self.r.rpop("input", 10)
        print(new_requests)
        assert isinstance(new_requests, list), new_requests
        assert len(new_requests) == 1, new_requests
        
    async def asyncTearDown(self) -> None:
        await self.r.flushdb()
            

class TestRedisMessageBroker(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self) -> None:
        self.r = await redis.from_url("redis://localhost/1")
        self.msg_broker = RedisMessageBroker(self.r)
        
                
        