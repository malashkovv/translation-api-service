import os
import aiohttp
import uvloop
import asyncio

from aiohttp import web
from aiohttp_swagger import setup_swagger
from aws_xray_sdk.ext.aiohttp.client import aws_xray_trace_config

from aws_xray_sdk.ext.aiohttp.middleware import middleware as xray_middleware
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.async_context import AsyncContext


asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def is_xray_on():
    return os.environ.get('XRAY', 'false') == 'true'


def create_session():
    if is_xray_on():
        trace_config = aws_xray_trace_config()
        return aiohttp.ClientSession(trace_configs=[trace_config])
    return aiohttp.ClientSession()


async def real_translate(text):
    req = "https://translate.google.com:443/translate_a/single?client=a&ie=utf-8&oe=utf-8&dt=t&sl=en&tl=ru&q={text}"
    async with create_session() as sess:
        async with sess.get(req.format(text=text)) as resp:
            if resp.status != 200:
                if resp.status == 429:
                    raise web.HTTPTooManyRequests(text="Too many requests for Google API.")
                else:
                    raise web.HTTPServiceUnavailable(text=f"Google API returned code: {resp.status}")
            text = await resp.json()
            return text[0][0][0]


async def fake_translate(text):
    return text[::-1]


translate = fake_translate


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
    translated_text = await translate(text) if text else ""
    return aiohttp.web.json_response({"translation": translated_text})


async def init_func(argv=None):
    middlewares = list()
    if is_xray_on():
        xray_recorder.configure(
            service="translation-api",
            sampling=False,
            context=AsyncContext(),
            daemon_address="xray-aws-xray:2000"
        )
        middlewares.append(xray_middleware)
    app = aiohttp.web.Application(middlewares=middlewares)
    app.add_routes([aiohttp.web.get('/translate', handle)])
    setup_swagger(app)
    return app


if __name__ == '__main__':
    web.run_app(init_func())
