from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Self

dot_env_path = str(Path(__file__).parent.parent / '.env')


class MinioSettings(BaseSettings):
    access_key: str
    secret_key: str
    bucket_name: str
    root_user: str
    root_password: str
    port: int
    port_secure: int
    endpoint: str


class PostgresSettings(BaseSettings):
    host: str
    port: int
    db: str
    user: str
    password: str
    version: int

    db_dsn: str = ''
    db_dsn_sync: str = ''

    @model_validator(mode='after')
    def db_dsn_validate(self) -> Self:
        self.db_dsn = (f'postgresql+asyncpg://'
                       f'{self.user}:{self.password}@'
                       f'{self.host}:{self.port}/'
                       f'{self.db}')

        self.db_dsn_sync = (f'postgresql+psycopg://'
                            f'{self.user}:{self.password}@'
                            f'{self.host}:{self.port}/'
                            f'{self.db}')
        return self


class TelegramSettings(BaseSettings):
    bot_token: str
    channel_id: str
    channel_name: str


class AttachmentSettings(BaseSettings):
    max_size: int
    extensions: List[str]


class Settings(BaseSettings):

    # MinIO
    minio: MinioSettings

    # PostgreSQL
    postgres: PostgresSettings

    # Telegram
    telegram: TelegramSettings

    # Attachments
    attachment: AttachmentSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter='__',
        env_file=dot_env_path,
        env_file_encoding='utf-8',
        extra='ignore')


settings = Settings()  # type: ignore