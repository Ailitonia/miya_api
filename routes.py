from aiohttp.web import Application
from view import index
from pixiv_utils import pixiv_illust, pixiv_illust_withb64, pixiv_rank
from pixivision_utils import pixivision
from nhentai_utils import nhentai_search, nhentai_download, nhentai_get


def setup_routes(app: Application):
    app.router.add_get('/', index)
    app.router.add_get('/api/pixiv/rank/', pixiv_rank)
    app.router.add_get('/api/pixiv/search/', pixiv_illust)
    app.router.add_get('/api/pixiv/download/', pixiv_illust_withb64)
    app.router.add_get('/api/pixivsion/', pixivision)
    app.router.add_get('/api/nhentai/search/', nhentai_search)
    app.router.add_get('/api/nhentai/download/', nhentai_download)
    app.router.add_get('/api/nhentai/get/', nhentai_get)
