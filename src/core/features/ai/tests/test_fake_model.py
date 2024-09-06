import unittest
import pytest
from src.core.features.ai.fake_model import FakeModel
from src.core.common import exceptions as ex

class TestFakeModel(unittest.IsolatedAsyncioTestCase):
    
    async def test_should_return_same_list_length(self):
        model = FakeModel()
        requests = ["1", "2", "3"]
        responses = await model(requests)
        assert len(responses) == len(requests)
        
    async def test_should_raise_error_if_string_is_empty(self):
        model = FakeModel()
        requests = ["1", "", "3"]
        with pytest.raises(ex.InvalidInputError):
            await model(requests)
            
    async def test_should_raise_error_if_string_is_longer_than_max_length(self):
        model = FakeModel(max_nb_characters=5)
        requests = ["This request is too long wow"]
        with pytest.raises(ex.InvalidInputError):
            await model(requests)
            
    async def test_should_raise_error_if_nb_words_is_more_than_max_words(self):
        model = FakeModel(max_nb_words=2)
        requests = ["This request has too many words"]
        with pytest.raises(ex.InvalidInputError):
            await model(requests)
            
    async def test_should_return_string_with_more_than_min_words(self):
        model = FakeModel(response_min_nb_words=5)
        requests = ["A small request"]
        responses = await model(requests)
        nb_words = len(responses[0].split())
        assert nb_words >= 5
        
    async def test_same_input_should_return_same_response(self):
        model = FakeModel(response_min_nb_words=5)
        requests = ["same request", "same request"]
        responses = await model(requests)
        assert responses[0] == responses[1]
        
    async def test_different_input_should_return_different_responses(self):
        model = FakeModel(response_min_nb_words=5)
        requests = ["a request", "a different request"]
        responses = await model(requests)
        assert responses[0] != responses[1]
        
    async def test_should_raise_error_if_too_many_requests(self):
        model = FakeModel(max_batch_size=2)
        requests = ["This", "is", "too", "many", "requests"]
        with pytest.raises(ex.InvalidInputError):
            await model(requests)