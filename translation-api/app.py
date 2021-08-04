from typing import Dict

import uvicorn
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from model import get_translator, Translator

app = FastAPI()


class TranslationResponse(BaseModel):
    translation: str


@app.get("/translate", response_model=TranslationResponse)
def predict(text: str, model: Translator = Depends(get_translator)):
    return TranslationResponse(translation=model.translate(text))


if __name__ == "__main__":
    uvicorn.run("translation-api.app:app", host="0.0.0.0", port=80, reload=True, log_level="debug")