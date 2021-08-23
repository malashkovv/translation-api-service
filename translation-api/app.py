import uvicorn
from fastapi import Depends, FastAPI
from pydantic import BaseModel

from .config import settings
from .model import Translator, get_translator

app = FastAPI()


class TranslationResponse(BaseModel):
    translation: str


@app.get("/translate", response_model=TranslationResponse)
def translate(text: str, model: Translator = Depends(get_translator)):
    return TranslationResponse(translation=model.translate(text))


@app.get("/health")
def health(model: Translator = Depends(get_translator)):
    return {
        "alive": True,
        "pytorch_device": model.device,
        "settings": {"translation_model_code": settings.translation_model_code},
    }


if __name__ == "__main__":
    uvicorn.run(
        "translation-api.app:app",
        host="0.0.0.0",
        port=80,
        reload=True,
        log_level="debug",
    )
