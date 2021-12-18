import datetime as dt
from timeit import default_timer as timer
from typing import Optional
from uuid import uuid4, UUID

from pydantic import BaseModel
from pydantic import Field, constr

from translation.cache import Cache
from translation.log import logger
from translation.model import Translator
from translation.pubsub import Queue


class TranslationRecordModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    translated_at: Optional[dt.datetime]

    text: constr(max_length=1024)
    source_language: str
    destination_language: str
    translated_text: Optional[str]


def run_inference(translator: Translator, queue: Queue, cache: Cache, max_records=10):
    for messages in queue.pull(max_records=max_records):
        logger.info(f"Received {len(messages)} records.")
        start_time = timer()
        records = [TranslationRecordModel.parse_raw(message) for message in messages]
        translated_texts = translator.translate(
            texts=[record.text for record in records]
        )
        end_time = timer()
        logger.info(f"Translation took: {end_time - start_time} seconds.")
        translated_at = dt.datetime.utcnow()
        for record, translated_text in zip(records, translated_texts):
            record.translated_at = translated_at
            record.translated_text = translated_text
            logger.debug(f"Putting message {record.id}: {translated_text}")
            cache.set(key=f"translation.{record.id}", value=record.json())
