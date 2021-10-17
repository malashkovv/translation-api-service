from functools import partial
from typing import Optional

import backoff
from fastapi import APIRouter, HTTPException

from api.cache import cache
from api.pubsub import queue
from api.routers.models import (
    TranslationRecordModel,
    TranslationRequestModel,
    TranslationResponseModel,
    TranslationStatusEnum,
)

router = APIRouter(tags=["translation"])


class NoRecordException(RuntimeError):
    pass


async def submit_translation(translation_request: TranslationRequestModel):
    record = TranslationRecordModel(**translation_request.dict())
    await queue.publish(
        topic=f"translation.{translation_request.source_language}-{translation_request.destination_language}",
        value=record.json(),
    )
    await cache.set(f"translation.{record.id}", value=record.json())
    return record


async def get_translation(translation_id: str) -> Optional[TranslationRecordModel]:
    raw_data = await cache.get(f"translation.{translation_id}")
    if raw_data is not None:
        return TranslationRecordModel.parse_raw(raw_data)


@backoff.on_exception(partial(backoff.expo, factor=0.05), NoRecordException)
async def poll_translation(record_id) -> TranslationRecordModel:
    record = await get_translation(record_id)
    if record is not None and record.translated_text is not None:
        return record
    else:
        raise NoRecordException(f"No record {record_id} yet!")


@router.post("/translate", response_model=TranslationResponseModel)
async def translate_action(
    translation_submit: TranslationRequestModel
) -> TranslationResponseModel:
    record = await submit_translation(translation_submit)
    translated_record = await poll_translation(record.id)
    return TranslationResponseModel(
        id=record.id,
        status=TranslationStatusEnum.translated,
        translated_text=translated_record.translated_text,
        text=translated_record.text,
        source_language=translated_record.source_language,
        destination_language=translated_record.destination_language,
    )


@router.post("/translation", response_model=TranslationResponseModel)
async def translation_create(
    translation_submit: TranslationRequestModel
) -> TranslationResponseModel:
    record = await submit_translation(translation_submit)
    return TranslationResponseModel(
        id=record.id,
        status=TranslationStatusEnum.submitted,
        text=record.text,
        source_language=record.source_language,
        destination_language=record.destination_language,
    )


@router.get("/translation/{translation_id}", response_model=TranslationResponseModel)
async def translate_retrieve(translation_id: str) -> TranslationResponseModel:
    record = await get_translation(translation_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Translation submission not found.")
    else:
        status = (
            TranslationStatusEnum.submitted
            if record.translated_text is None
            else TranslationStatusEnum.translated
        )
        return TranslationResponseModel(
            id=record.id,
            status=status,
            text=record.text,
            source_language=record.source_language,
            destination_language=record.destination_language,
            translated_text=record.translated_text,
        )
