import torch
from transformers import MarianMTModel, MarianTokenizer


class Translator:
    def __init__(self, tokenizer, model, device_type="cpu"):
        self.model = model
        self.tokenizer = tokenizer
        self._device = torch.device(device_type)
        self.model.to(self._device)

    @property
    def device(self):
        """Low-level info about device used by PyTorch."""
        return self._device.type

    @classmethod
    def initialize(cls, code: str, device_type="cpu"):
        tokenizer = MarianTokenizer.from_pretrained(f"Helsinki-NLP/opus-mt-{code}")
        model = MarianMTModel.from_pretrained(
            f"Helsinki-NLP/opus-mt-{code}", torchscript=True
        )
        return cls(tokenizer, model, device_type)

    def translate(self, texts):
        with torch.inference_mode():
            tokenized_text_tensor = self.tokenizer(
                texts, return_tensors="pt", padding="longest"
            )

            tokenized_text_tensor.to(self._device)

            translation_tensor = self.model.generate(**tokenized_text_tensor)
            translated_texts = self.tokenizer.batch_decode(
                translation_tensor, skip_special_tokens=True
            )

            # Clean up memory
            del translation_tensor
            del tokenized_text_tensor
            if self.device == "cuda":
                torch.cuda.empty_cache()

            return translated_texts
