from common.storages.db.repositories import RequestRepository
from common.storages.cache.redis import RedisCacheStorage
from common.config import get_message_broker, settings
from common import exceptions as ex
from common.enums import RequestStatus
from ai.src.fake_model import FakeModel
import redis.asyncio as redis
import asyncio
import time
import logging
from sqlalchemy.ext.asyncio import create_async_engine

logger = logging.getLogger("AI")
logging.basicConfig(filename='ai.log', level=logging.INFO)

async def main(repo : RequestRepository):
    redis_engine = await redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True)
    cache = RedisCacheStorage(redis_engine, settings.CACHE_DURATION_MINUTES)
    message_broker = await get_message_broker()
    model = FakeModel(max_nb_characters=settings.MAX_NB_CHARACTERS_IN_REQUEST, max_batch_size=settings.BATCH_SIZE, min_duration=settings.MODEL_INFERENCE_MIN_DURATION, max_duration=settings.MODEL_INFERENCE_MAX_DURATION, simulate_duration=True, response_max_nb_words=settings.MAX_NB_WORDS_IN_RESPONSE)
    logger.info('AI ready, waiting request to process')
    while True:
        requests = await message_broker.receive_requests(model.max_batch_size)
        if len(requests) > 0:
            await repo.update_requests_status(requests, RequestStatus.IN_PROCESS)
            print(f"received {len(requests)} requests")
            inputs = [request["input"] for request in requests]
            print("inputs: ")
            print(inputs)
            try:
                output = await model(inputs)
                
                responses = [{"job_id":requests[i]["job_id"], "request_id": requests[i]["request_id"],"input":requests[i]["input"], "output":output[i], "user_id":requests[i]["user_id"]} for i in range(len(requests))]
                await repo.save_responses(responses)
                for response in responses:
                    await cache.store(response["input"], response["output"])
                #await message_broker.send_responses(responses)
            except ex.InvalidInputError as e:
                logger.warning(f"InvalidInputError: {e}")
                await repo.update_requests_status(requests, RequestStatus.FAILED)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await repo.update_requests_status(requests, RequestStatus.FAILED)
        time.sleep(1)
            
if __name__ == "__main__":
    try:
        engine = create_async_engine(f"postgresql+asyncpg://{settings.POSTGRESSQL_USER}:{settings.POSTGRESQL_PASSWORD}@{settings.POSTGRESQL_HOST}/{settings.POSTGRESQL_DB}", echo=True)
        repo = RequestRepository(engine)
        asyncio.run(main(repo))
    except KeyboardInterrupt:
        logger.info('AI interrupted manually')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        engine.dispose()
        logger.info('AI shutting down')