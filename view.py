from aiohttp import web
from aiohttp.web_request import Request


async def index(request: Request):
    return web.Response(text='Hello Aiohttp!')
