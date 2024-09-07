from common.message_brokers.interfaces import Response
from common.config import get_message_broker, settings
from ai.src.fake_model import FakeModel
import asyncio
import time
async def main():
    message_broker = await get_message_broker()
    model = FakeModel(max_nb_characters=settings.MAX_NB_CHARACTERS_IN_REQUEST, max_nb_words=settings.MAX_NB_WORDS_IN_REQUEST, max_batch_size=settings.MAX_BATCH_SIZE, min_duration=settings.MODEL_INFERENCE_MIN_DURATION, max_duration=settings.MODEL_INFERENCE_MAX_DURATION, simulate_duration=True, response_min_nb_words=settings.MIN_NB_WORDS_IN_RESPONSE)
    
    while True:
        requests = await message_broker.receive_requests(model.max_batch_size)
        if len(requests) > 0:
            print(f"received {len(requests)} requests")
            inputs = [request["input"] for request in requests]
            responses = await model(inputs)
            await message_broker.send_responses([{"input":requests[i]["input"], "output":responses[i], "user_id":requests[i]["user_id"]} for i in range(len(requests))])
        time.sleep(1)
            
if __name__ == "__main__":
    asyncio.run(main())