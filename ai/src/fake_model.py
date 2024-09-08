from common import exceptions as ex
import time
import random

class FakeModel:
    def __init__(self, max_nb_characters : int = 1024, response_max_nb_words: int = 1000, max_batch_size : int = 16, min_duration : int = 30, max_duration = 60, simulate_duration : bool = False) -> None:
        self.max_nb_characters = max_nb_characters
        self.response_max_nb_words = response_max_nb_words
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.simulate_duration = simulate_duration
        self.max_batch_size = max_batch_size
    
    async def __call__(self, requests : list[str]) -> list[str]:
        if len(requests) > self.max_batch_size:
            raise ex.InvalidInputError(f"Too many requests (maximum {self.max_batch_size})")
        responses = []
        for request in requests:
            if len(request) == 0:
                raise ex.InvalidInputError("Request should not be empty string")
            
            if len(request) > self.max_nb_characters:
                raise ex.InvalidInputError(f"Request should be maximum {self.max_nb_characters} characters")
            print(request)
            response = request + " " + "word " * self.response_max_nb_words
            responses.append(" ".join((response.split())[0:self.response_max_nb_words]))
        if self.simulate_duration:
            time.sleep(random.random()*(self.max_duration-self.min_duration)+self.min_duration)
        return responses