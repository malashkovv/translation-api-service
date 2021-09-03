import typer

from translation.cache import Cache
from translation.inference import run_inference
from translation.model import Translator
from translation.pubsub import Queue

app = typer.Typer()


# @app.command()
def run(translation_code: str, torch_device: str):
    typer.echo(f"Queue: translation_{translation_code}")
    translator = Translator.initialize(code=translation_code, device_type=torch_device)
    queue = Queue.initialize(topic=f"translation_{translation_code}")
    cache = Cache.initialize()
    run_inference(translator, queue, cache)


if __name__ == "__main__":
    # app()
    run("en-ru", "cuda:0")
