from pydantic.v1 import BaseSettings
import logging

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJJc3N1ZXIiOiJJc3N1ZXIiLCJVc2VybmFtZSI6IkphdmFJblVzZSIsImV4cCI6MTcwNjg3MDY2NiwiaWF0IjoxNzA2ODcwNjY2fQ.uczx9svNhiC52m48UIyVlgP_TsNNPiu-INiAAe6RQ6w"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Token expiration time
    OPENAPI_KEY: str = "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"
    DATABASE_URL: str = "postgresql://postgres:postgres@db/mydatabase"
    RABBITMQ_URL: str  = "amqp://user:password@rabbitmq/%2F"
    SSL_CERT_FILE: str  = "certificates/cert.pem"
    SSL_KEY_FILE: str  = "certificates/key.pem"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"

settings = Settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
