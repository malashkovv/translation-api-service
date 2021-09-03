import logging

import typer

from translation.cache import Cache
from translation.config import settings
from translation.inference import run_inference
from translation.log import logger
from translation.model import Translator
from translation.pubsub import Queue

app = typer.Typer()


@app.command()
def run(translation_code: str, ttl: int = 60 * 30, debug: bool = False):
    if debug:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Queue: translation_{translation_code}.")
    translator = Translator.initialize(
        code=translation_code, device_type=settings.torch_device
    )
    logger.info(f"Model {translation_code} is initialized.")
    queue = Queue.initialize(
        urls=settings.kafka_urls, topic=f"translation_{translation_code}"
    )
    cache = Cache.initialize(url=settings.redis_url, ttl=ttl)
    run_inference(translator, queue, cache)


if __name__ == "__main__":
    app()
