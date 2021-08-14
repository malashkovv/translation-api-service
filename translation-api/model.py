import torch
from .log import logger
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from .config import settings


class Translator:
    def __init__(self, tokenizer, model):
        self.model = model
        self.tokenizer = tokenizer

    @classmethod
    def initialize(cls, code):
        tokenizer = AutoTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{code}")
        model = AutoModelForSeq2SeqLM.from_pretrained(
            f"Helsinki-NLP/opus-mt-{code}", torchscript=True
        )
        return cls(tokenizer, model)

    @property
    def device(self):
        if torch.cuda.is_available():
            device_type = "cuda:0"
        else:
            device_type = "cpu"
            logger.warning("No cuda device is found! Using CPU instead. ")
        return torch.device(device_type)

    def translate(self, text):
        tokenized_text = self.tokenizer([text], return_tensors="pt")
        tokenized_text.to(self.device)

        translation = self.model.generate(**tokenized_text)
        return self.tokenizer.batch_decode(translation, skip_special_tokens=True)[0]


translator = Translator.initialize(settings.translation_model_code)


def get_translator():
    return translator
