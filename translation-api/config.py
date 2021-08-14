from pydantic import BaseSettings


class Settings(BaseSettings):
    translation_model_code = 'en-de'


settings = Settings()