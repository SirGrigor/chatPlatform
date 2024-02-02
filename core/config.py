from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time

    DATABASE_URL: str  # SQLAlchemy database URL
    RABBITMQ_URL: str  # RabbitMQ connection URL

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
