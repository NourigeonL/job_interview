from storages.db.repositories import RequestRepository
from storages.cache.redis import RedisCacheStorage
from message_brokers.redis import RedisMessageBroker
from common.config import settings
from common.enums import RequestStatus
import redis.asyncio as redis
import asyncio
import time
from common.logger import Logger
from sqlalchemy.ext.asyncio import create_async_engine

logger = Logger(name="Response Handler", prefix="response_handler", log_level=settings.LOG_LEVEL, log_dir="./logs").get_logger()

async def main(repo : RequestRepository):
    async with redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True) as redis_engine:
        redis_engine = await redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True)
        cache = RedisCacheStorage(redis_engine, settings.CACHE_DURATION_MINUTES)
        message_broker = RedisMessageBroker(await redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True))
        logger.info('Response Handler, waiting reponses to process')
        while True:
            responses = await message_broker.receive_reponses(settings.BATCH_SIZE)
            if len(responses) > 0:
                await process_responses(repo, cache, responses)
            time.sleep(1)

async def process_responses(repo: RequestRepository, cache : RedisCacheStorage, responses):
    failed_requests = []
    completed_responses = []
    in_process_requests = []
    for response in responses:
        if response["status"] == RequestStatus.FAILED:
            failed_requests.append(response)
        elif response["status"] == RequestStatus.IN_PROCESS:
            in_process_requests.append(response)
        else:
            completed_responses.append(response)
            await cache.store(response["input"], response["output"])
    if len(completed_responses) > 0:
        await repo.save_responses(completed_responses)
        logger.info(f"Saved and cached {len(completed_responses)} responses")
    if len(failed_requests) > 0:
        await repo.update_requests_status(failed_requests, RequestStatus.FAILED)
        logger.info(f"{len(failed_requests)} requests failed while being processed by the AIs")
    if len(in_process_requests) > 0:
        await repo.update_requests_status(in_process_requests, RequestStatus.IN_PROCESS)
        logger.info(f"{len(in_process_requests)} requests are being processed by the AIs")
        
if __name__ == "__main__":
    engine = create_async_engine(settings.ASYNC_DATABASE_URI, echo=True)
    repo = RequestRepository(engine)
    try:
        asyncio.run(main(repo))
    except KeyboardInterrupt:
        logger.info('AI interrupted manually')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        asyncio.run(engine.dispose())
        logger.info('AI shutting down')