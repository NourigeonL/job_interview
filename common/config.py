from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import redis.asyncio as redis
class Settings(BaseSettings):
    
    model_config = ConfigDict(case_sensitive = True, env_file="./.env")
    
    MODEL_INFERENCE_MIN_DURATION : int = 0
    MODEL_INFERENCE_MAX_DURATION : int = 0
    BATCH_SIZE : int = 0
    MAX_NB_REQUESTS : int = 0
    MAX_NB_CHARACTERS_IN_REQUEST : int = 0
    MAX_NB_WORDS_IN_REQUEST : int = 0
    MAX_NB_WORDS_IN_RESPONSE : int = 1000
    REDIS_HOST : str = "redis://localhost/0"
    CACHE_DURATION_MINUTES : int = 10
    POSTGRESQL_HOST : str = "localhost"
    POSTGRESSQL_USER : str = "admin"
    POSTGRESQL_PASSWORD : str = "admin"
    POSTGRESQL_DB : str  = "db"
    JWT_SECRET : str = ""
    LOG_LEVEL : str = "DEBUG"
    
settings = Settings()