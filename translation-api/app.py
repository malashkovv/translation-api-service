from aiohttp import web
from translate import translator


async def handle(request):
    text = request.match_info.get('text', "")
    translated_text = translator("en", "ru", text)
    return web.json_response({"translation": translated_text})


def init_func(argv):
    app = web.Application()
    app.add_routes([web.get('/translate', handle)])
    return app