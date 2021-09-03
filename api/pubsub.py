import asyncio
import json
from typing import Optional

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from api.config import settings


class Queue:
    def __init__(self, urls):
        self.urls = urls
        self.kafka_producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        loop = asyncio.get_event_loop()
        self.kafka_producer = AIOKafkaProducer(
            loop=loop, client_id="API", bootstrap_servers=self.urls
        )
        await self.kafka_producer.start()

    async def publish(self, topic: str, value: BaseModel):
        return await self.kafka_producer.send(
            topic, json.dumps(value.dict()).encode("utf-8")
        )

    async def stop(self):
        if self.kafka_producer is not None:
            await self.kafka_producer.stop()


queue = Queue(urls=settings.kafka_urls)
