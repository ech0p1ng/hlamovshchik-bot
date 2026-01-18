from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Self
from dotenv import load_dotenv

ENV_PATH = str(Path(__file__).parent.parent / '.env')


class MinioSettings(BaseSettings):
    access_key: str
    secret_key: str
    bucket_name: str
    root_user: str
    root_password: str
    port: int
    port_secure: int
    endpoint: str
    endpoint_secure: str
    ip: str
    domain: str
    admin_domain: str


class PostgresSettings(BaseSettings):
    host: str
    port: int
    db: str
    user: str
    password: str
    version: int
    dump_timeout_seconds: int

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
    chat_id: int


class AttachmentSettings(BaseSettings):
    max_size: int
    extensions: List[str]
    video_extensions: List[str]
    image_extensions: List[str]


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
        env_file=ENV_PATH,
        env_file_encoding='utf-8',
        extra='ignore')


__settings: Settings | None = None


def get_settings() -> Settings:
    global __settings
    if __settings is None:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        __settings = Settings()  # type: ignore
    return __settings
