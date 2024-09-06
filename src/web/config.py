from pydantic_settings import BaseSettings
from pydantic import ConfigDict
class Settings(BaseSettings):
    
    model_config = ConfigDict(case_sensitive = True, env_file="./.env")
    
    MODEL_INFERENCE_MIN_DURATION : int = 30
    MODEL_INFERENCE_MAX_DURATION : int = 60
    MAX_BATCH_SIZE : int = 16
    MAX_NB_CHARACTERS_IN_REQUEST : int = 1024
    MAX_NB_WORDS_IN_REQUEST : int = 1000
    MIN_NB_WORDS_IN_RESPONSE : int = 1000