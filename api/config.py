from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    kafka_urls = "kafka:9092"
    redis_url = "redis://redis:6379"
    redis_ttl: int = 60 * 30

    @validator("kafka_urls")
    def split_kafka_urls(cls, v):
        return v.split(",")


settings = Settings()
