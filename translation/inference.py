from timeit import default_timer as timer

from translation.cache import Cache
from translation.log import logger
from translation.model import Translator
from translation.pubsub import Queue


def run_inference(translator: Translator, queue: Queue, cache: Cache):
    for message_batch in queue.pull():
        logger.info(f"Received {len(message_batch)} records.")
        start_time = timer()
        translated_texts = translator.translate(
            texts=[message["record"]["text"] for message in message_batch]
        )
        end_time = timer()
        logger.info(f"Translation took: {end_time - start_time} seconds.")
        for message, translated_text in zip(message_batch, translated_texts):
            logger.debug(f"Putting message {message['id']}: {translated_text}")
            cache.set(
                key=f"translation_{message['id']}",
                value={"translation": translated_text},
            )
