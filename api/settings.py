import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# 프로젝트 루트 디렉토리의 .env를 사용
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)


class Settings(BaseSettings):
    """backend 공통 설정을 환경변수와 .env로부터 읽음"""

    # Database
    db_host: str = Field(validation_alias="DB_HOST", default="localhost")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")
    db_name: str = Field(validation_alias="DB_NAME")

    # Elasticsearch
    es_host: str = Field("localhost", validation_alias="ES_HOST")
    es_port: str = Field("9200", validation_alias="ES_PORT")

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def async_database_url(self) -> str:
        """Return async SQLAlchemy URL (using asyncmy driver)."""
        return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}/{self.db_name}"
