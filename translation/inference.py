import logging

from translation.cache import Cache
from translation.model import Translator
from translation.pubsub import Queue


def run_inference(translator: Translator, queue: Queue, cache: Cache):
    for message_batch in queue.pull():
        logging.info(f"Got record batch: {len(message_batch)}")
        translated_texts = translator.translate(
            [message["record"]["text"] for message in message_batch]
        )
        for message, translated_text in zip(message_batch, translated_texts):
            cache.set(
                key=f"translation_{message['id']}",
                value={"translation": translated_text},
            )
