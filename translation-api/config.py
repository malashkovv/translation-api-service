from pydantic import BaseSettings


class Settings(BaseSettings):
    translation_model_code = "en-de"
    torch_device = "cuda:0"


settings = Settings()
