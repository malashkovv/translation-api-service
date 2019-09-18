import requests

from aiohttp import web
from translate import translator


def translate(text):
    try:
        return translator("en", "ru", text)[0][0][0]
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code == 429:
            raise web.HTTPTooManyRequests(text="Too many requests to Google API translation service.")
        raise


async def handle(request):
    text = request.rel_url.query.get('text', "")
    translated_text = translate(text) if text else ""
    return web.json_response({"translation": translated_text})


def init_func(argv=None):
    app = web.Application()
    app.add_routes([web.get('/translate', handle)])
    return app


if __name__ == '__main__':
    web.run_app(init_func())