from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pedidos.db"
    catalogo_base_url: str = "http://localhost:8002"
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

