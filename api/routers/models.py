import datetime as dt
from enum import Enum
from typing import Optional
from uuid import uuid4, UUID

from pydantic import BaseModel, Field, constr, validator


class TranslationRequestModel(BaseModel):
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


class TranslationStatusEnum(str, Enum):
    submitted = "submitted"
    translated = "translated"


class TranslationResponseModel(BaseModel):
    id: UUID
    text: constr(max_length=1024)
    source_language: str
    destination_language: str
    translated_text: Optional[str]
    status: TranslationStatusEnum


class TranslationRecordModel(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    translated_at: Optional[dt.datetime]

    text: constr(max_length=1024)
    source_language: str
    destination_language: str
    translated_text: Optional[str]
