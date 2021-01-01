import re
from config import API_KEY
from logger import logger
from aiohttp.web_request import Request
from aiohttp.web import json_response
from .utils import fetch_json, fetch_text, Pixivision


async def pixivision(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'aid', 'mode']:
            response = json_response(data={'error': True, 'body': 'Illegal parameters'}, status=403)
            return response
    key = data.get('key')
    if key not in API_KEY:
        response = json_response(data={'error': True, 'body': 'Unauthorized access'}, status=403)
        return response
    mode = data.get('mode')
    if mode not in ['illustration', 'article']:
        response = json_response(data={'error': True, 'body': 'Illegal parameters'}, status=403)
        return response

    try:
        illustration = Pixivision()
        if mode == 'illustration':
            _res = await illustration.get_illustration_list()
            response = json_response(data=_res, status=200)
            return response
        elif mode == 'article':
            aid = data.get('aid')
            if not aid:
                response = json_response(data={'error': True, 'body': 'Missing parameters'}, status=400)
                return response
            if re.match(r'^\d+$', aid):
                _res = await illustration.get_article_info(aid=aid)
                response = json_response(data=_res, status=200)
                return response
        else:
            response = json_response(data={'error': True, 'body': 'Missing or illegal parameters'}, status=400)
            return response
    except Exception as e:
        aid = data.get('aid')
        logger.error(f'{__name__}: mode: {mode}, article: {aid}, pixivision error: {repr(e)}')
        response = json_response(data={'error': True, 'body': 'Server error'}, status=500)
        return response
