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
from common.logger import Logger
from sqlalchemy.ext.asyncio import create_async_engine

logger = Logger(name="ai", prefix="ai", log_level=settings.LOG_LEVEL, log_dir="./logs").get_logger()

async def main():
    message_broker = await get_message_broker()
    model = FakeModel(max_nb_characters=settings.MAX_NB_CHARACTERS_IN_REQUEST, max_batch_size=settings.BATCH_SIZE, min_duration=settings.MODEL_INFERENCE_MIN_DURATION, max_duration=settings.MODEL_INFERENCE_MAX_DURATION, simulate_duration=True, response_max_nb_words=settings.MAX_NB_WORDS_IN_RESPONSE)
    logger.info('AI ready, waiting request to process')
    while True:
        requests = await message_broker.receive_requests(model.max_batch_size)
        if len(requests) > 0:
            for request in requests:
                request["status"] = RequestStatus.IN_PROCESS
            await message_broker.send_responses(requests)
            logger.debug(f"received {len(requests)} requests")
            inputs = [request["input"] for request in requests]
            logger.debug(f"inputs: {inputs}")
            try:
                outputs = await model(inputs)
                logger.debug(f"outputs: {outputs}")
                for i in range(len(requests)):
                    requests[i]["status"] = RequestStatus.COMPLETED
                    requests[i]["output"]=outputs[i]
                await message_broker.send_responses(requests)
            except ex.InvalidInputError as e:
                logger.warning(f"InvalidInputError: {e}")
                for request in requests:
                    request["status"] = RequestStatus.FAILED
                await message_broker.send_responses(requests)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                for request in requests:
                    request["status"] = RequestStatus.FAILED
                await message_broker.send_responses(requests)
            time.sleep(1)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('AI interrupted manually')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info('AI shutting down')