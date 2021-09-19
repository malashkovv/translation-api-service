import uuid
from datetime import datetime
from functools import partial

import backoff
from fastapi import APIRouter
from pydantic import BaseModel, constr, validator

from api.cache import cache
from api.pubsub import queue

router = APIRouter(tags=["translation"])


class TranslationRequest(BaseModel):
    text: constr(max_length=1024)
    source_language: str
    destination_language: str

    @validator("source_language")
    def check_source_language(cls, v, values):
        if v in ["en", "de", "ru"]:
            return v
        elif v == values["destination_language"]:
            raise ValueError("Source language is the same as destination!")
        else:
            raise ValueError("Unsupported source language!")

    @validator("destination_language")
    def check_destination_language(cls, v, values):
        if v in ["en", "de", "ru"]:
            return v
        elif v == values["source_language"]:
            raise ValueError("Source language is the same as destination!")
        else:
            raise ValueError("Unsupported destination language!")


class TranslationRecord(BaseModel):
    record: TranslationRequest
    id: str
    timestamp: str


class TranslationResponse(BaseModel):
    translated_text: str


class NoRecordException(RuntimeError):
    pass


@backoff.on_exception(partial(backoff.expo, factor=0.05), NoRecordException)
async def poll_result(record_id):
    record = await cache.get(f"translation_{record_id}")
    if record is not None:
        return record
    else:
        raise NoRecordException(f"No record {record_id} yet!")


@router.post("/translate", response_model=TranslationResponse)
async def submit_translation(translation_submit: TranslationRequest):
    record_id = str(uuid.uuid4())
    record = TranslationRecord(
        record=translation_submit, timestamp=str(datetime.utcnow()), id=record_id
    )
    await queue.publish(
        topic=f"translation_{translation_submit.source_language}-{translation_submit.destination_language}",
        value=record,
    )

    translated_record = await poll_result(record_id)
    return TranslationResponse(translated_text=translated_record["translation"])
