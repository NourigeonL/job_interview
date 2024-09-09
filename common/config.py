from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator, ValidationInfo, PostgresDsn
from urllib.parse import quote
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
    POSTGRESQL_USER : str = "admin"
    POSTGRESQL_PASSWORD : str = "admin"
    POSTGRESQL_DB : str  = "db"
    POSTGRESQL_PORT: int = 5432
    JWT_SECRET : str = ""
    LOG_LEVEL : str = "DEBUG"
    ASYNC_DATABASE_URI : str = ""

    @field_validator("ASYNC_DATABASE_URI", mode='before')
    def assemble_db_uri(cls, v: str | None, values: ValidationInfo) -> str:

        return str(PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.data["POSTGRESQL_USER"],
            password=quote(values.data["POSTGRESQL_PASSWORD"]),
            host=values.data["POSTGRESQL_HOST"],
            port=values.data["POSTGRESQL_PORT"],
            path=values.data['POSTGRESQL_DB']
        ))
    
settings = Settings()