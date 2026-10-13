import os.path
from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MAX_IMAGE_SIZE = 1024 * 1024 * 5 # 5 MB
MAX_FILE_SIZE = 1024 * 1024 * 100 # 100 MB


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"), env_file_encoding="utf-8"
    )
    secret_key: SecretStr

    #Database
    database_url: str
    postgres_db : str
    postgres_user : str
    postgres_password : str
    redis_host : str
    redis_port : str
    redis_username : str
    redis_password : SecretStr

    # Authentication
    access_token_expire_minutes: int = 200
    reset_token_expire_minutes: int = 400
    algorithm: str = "HS256"

    # Document processing
    max_image_size: int = MAX_IMAGE_SIZE
    max_file_size: int = MAX_FILE_SIZE

    # Email send
    mail_from: str = ""
    mail_host: str = ""
    mail_port: int = 2525
    mail_username: str = ""
    mail_password: str = ""
    mail_tls: bool = True

    # External services
    frontend_url: str = "http://localhost:5173"
    s3_bucket_name: str = ""
    s3_region: str = "us-east-1"
    s3_access_key_id: SecretStr | None = None
    s3_secret_access_key: SecretStr | None = None
    s3_endpoint_url: str | None = None

    # AI Services
    llama_api_key: str | None = None
    primary_model: str = "gpt-4o-mini"
    openai_key: str | None = ""
    max_retries : int = 3

    # Application configs
    app_env : str = "development"
    langsmith_tracing : str = ""
    rate_limit : str = "20/minute"

    @property
    def is_production(self)->bool:
        return self.app_env == "production"



settings = Settings()


@lru_cache
def get_settings() -> Settings:
    """ Cached Settings instance - loaded once, reused everywhere.
        Prevents reading the env file at every request.
    """
    return Settings()
