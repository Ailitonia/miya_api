from aiohttp.web import Application
from view import index
from pixiv_utils import pixiv_illust, pixiv_illust_withb64, pixiv_rank
from pixivision_utils import pixivsion


def setup_routes(app: Application):
    app.router.add_get('/', index)
    app.router.add_get('/api/pixiv/rank/', pixiv_rank)
    app.router.add_get('/api/pixiv/search/', pixiv_illust)
    app.router.add_get('/api/pixiv/download/', pixiv_illust_withb64)
    app.router.add_get('/api/pixivsion/', pixivsion)
