from common.config import settings
from message_brokers.redis import RedisMessageBroker
from message_brokers.interfaces import IMessageBroker, RequestDict
from common import exceptions as ex
from common.enums import RequestStatus
from ai.src.fake_model import FakeModel
import asyncio
import time
from common.logger import Logger
import redis.asyncio as redis

logger = Logger(name="ai", prefix="ai", log_level=settings.LOG_LEVEL, log_dir="./logs").get_logger()

async def main():
    message_broker = RedisMessageBroker(await redis.from_url(settings.REDIS_HOST, encoding="utf-8", decode_responses=True))
    model = FakeModel(max_nb_characters=settings.MAX_NB_CHARACTERS_IN_REQUEST, max_batch_size=settings.BATCH_SIZE, min_duration=settings.MODEL_INFERENCE_MIN_DURATION, max_duration=settings.MODEL_INFERENCE_MAX_DURATION, simulate_duration=True, response_max_nb_words=settings.MAX_NB_WORDS_IN_RESPONSE)
    logger.info('AI ready, waiting request to process')
    while True:
        requests = await message_broker.receive_requests(model.max_batch_size)
        if len(requests) > 0:
            await process_requests(message_broker, model, requests)
            time.sleep(1)

async def process_requests(message_broker : IMessageBroker, model : FakeModel, requests : list[RequestDict]):
    await notify_response_handler(message_broker, requests, RequestStatus.IN_PROCESS)
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
        await notify_response_handler(message_broker, requests, RequestStatus.FAILED)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await notify_response_handler(message_broker, requests, RequestStatus.FAILED)

async def notify_response_handler(message_broker : IMessageBroker, requests : list[RequestDict], status : RequestStatus):
    for request in requests:
        request["status"] = status
    await message_broker.send_responses(requests)
        
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('AI interrupted manually')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info('AI shutting down')