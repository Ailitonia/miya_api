from aiohttp import web
from logger import logger
from routes import setup_routes


app = web.Application()
setup_routes(app)
web.run_app(app, host='127.0.0.1', port=9090, access_log=logger)
