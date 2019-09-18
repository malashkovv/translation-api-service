import requests

from aiohttp import web
from aiohttp_swagger import setup_swagger
from translate import translator


def translate(text):
    try:
        return translator("en", "ru", text)[0][0][0]
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == 429:
            raise web.HTTPTooManyRequests(text="Too many requests to Google API translation service.")
        raise


async def handle(request):
    """
    ---
    description: This end-point allows to translate from English to Russian using Google API services
    tags:
    - translation
    produces:
    - application/json
    parameters:
        - in: query
          name: text
          required: false
          schema:
            type: string
          description: Text for translation
    responses:
        "200":
            description: successful operation. Return translated text
        "405":
            description: invalid HTTP Method
        "429":
            description: Too many requests (Google API has restriction on how many calls you can do.)
    """
    text = request.rel_url.query.get('text', "")
    translated_text = translate(text) if text else ""
    return web.json_response({"translation": translated_text})


def init_func(argv=None):
    app = web.Application()
    app.add_routes([web.get('/translate', handle)])
    setup_swagger(app)
    return app


if __name__ == '__main__':
    web.run_app(init_func())