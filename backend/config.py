import os.path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR,".env"),
        env_file_encoding="utf-8"
    )
    secret_key : SecretStr
    algorithm : str = "HS256"
    database_url: str
    access_token_expire_minutes: int = 200
    reset_token_expire_minutes: int = 400

    max_image_size : int = 1024 * 1024 * 5 # 5 MB
    max_file_size : int = 1024 * 1024 * 100 # 100 MB

    # Email send
    mail_from : str = ""
    mail_host : str = ""
    mail_port : int = 2525
    mail_username : str = ""
    mail_password : str = ""
    mail_tls : bool = True

    frontend_url : str = "http://localhost:5173"

    s3_bucket_name : str = ""
    s3_region : str = "us-east-1"
    s3_access_key_id : SecretStr | None = None
    s3_secret_access_key : SecretStr | None = None
    s3_endpoint_url: str | None = None
    llama_api_key : str | None= None

    openai_key : str | None = ""



settings = Settings()
