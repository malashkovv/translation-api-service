import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional

import aioredis
import uvicorn
from aiokafka import AIOKafkaProducer
from aioredis import Redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator

from api.config import settings

app = FastAPI()


class Cache:
    def __init__(self):
        self.redis_cache: Optional[Redis] = None

    async def start(self):
        self.redis_cache = await aioredis.from_url(
            "redis://redis:6379/0?encoding=utf-8"
        )

    async def keys(self, pattern):
        return await self.redis_cache.keys(pattern)

    async def set(self, key, value):
        return await self.redis_cache.set(key, json.loads(value))

    async def get(self, key):
        value = await self.redis_cache.get(key)
        return json.loads(value) if value else None

    async def stop(self):
        if self.redis_cache is not None:
            await self.redis_cache.close()


class Queue:
    def __init__(self):
        self.kafka_producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        loop = asyncio.get_event_loop()
        self.kafka_producer = AIOKafkaProducer(
            loop=loop, client_id="API", bootstrap_servers=settings.kafka_brokers
        )
        await self.kafka_producer.start()

    async def publish(self, topic: str, value: BaseModel):
        return await self.kafka_producer.send(
            topic, json.dumps(value.dict()).encode("utf-8")
        )

    async def stop(self):
        if self.kafka_producer is not None:
            await self.kafka_producer.stop()


cache = Cache()
queue = Queue()


@app.on_event("startup")
async def startup_event():
    await queue.start()
    await cache.start()


@app.on_event("shutdown")
async def shutdown_event():
    await queue.stop()
    await cache.stop()


class TranslationSubmitRequest(BaseModel):
    text: str
    source_language: str
    destination_language: str

    @validator("source_language")
    def check_source_language(cls, v, values):
        if v in ["en", "de", "ru"]:
            return v
        else:
            raise ValueError("Unsupported source language!")

    @validator("destination_language")
    def check_destination_language(cls, v, values):
        if v in ["en", "de", "ru"]:
            return v
        else:
            raise ValueError("Unsupported destination language!")


class TranslationSubmitRecord(BaseModel):
    record: TranslationSubmitRequest
    id: str
    timestamp: str


class TranslationSubmitResponse(BaseModel):
    id: str


class Translation(BaseModel):
    translated_text: str


@app.post("/translate", response_model=TranslationSubmitResponse)
async def submit_translation(translation_submit: TranslationSubmitRequest):
    record = TranslationSubmitRecord(
        record=translation_submit,
        timestamp=str(datetime.utcnow()),
        id=str(uuid.uuid4()),
    )
    await queue.publish(
        topic=f"translation_{translation_submit.source_language}-{translation_submit.destination_language}",
        value=record,
    )
    return TranslationSubmitResponse(id=record.id)


@app.get("/translate/{id}", response_model=Translation)
async def get_translation(id):
    record = await cache.get(f"translation_{id}")
    if record is not None:
        return Translation(translated_text=record["translation"])
    else:
        raise HTTPException(status_code=404, detail="Translation not found")


@app.get("/health")
def health():
    return {"alive": True}


if __name__ == "__main__":
    uvicorn.run("api.app:app", host="0.0.0.0", port=80, reload=True, log_level="debug")
