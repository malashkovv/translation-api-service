from pydantic import BaseSettings


class Settings(BaseSettings):
    kafka_brokers = "kafka:9092"


settings = Settings()
