import re
from config import API_KEY
from logger import logger
from aiohttp.web_request import Request
from aiohttp.web import json_response
from .utils import fetch_json, fetch_text, Pixivsion


async def pixivsion(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'aid', 'mode']:
            response = json_response(data={'error': 'Illegal parameters'}, status=403)
            return response
    key = data.get('key')
    if key not in API_KEY:
        response = json_response(data={'error': 'Unauthorized access'}, status=403)
        return response
    mode = data.get('mode')
    if mode not in ['illustration', 'article']:
        response = json_response(data={'error': 'Illegal parameters'}, status=403)
        return response

    try:
        illustration = Pixivsion()
        if mode == 'illustration':
            _res = await illustration.get_illustration_list()
            response = json_response(data=_res, status=200)
            return response
        elif mode == 'article':
            aid = data.get('aid')
            if not aid:
                response = json_response(data={'error': 'Missing parameters'}, status=400)
                return response
            if re.match(r'^\d+$', aid):
                _res = await illustration.get_article_info(aid=aid)
                response = json_response(data=_res, status=200)
                return response
        else:
            response = json_response(data={'error': 'Missing or illegal parameters'}, status=400)
            return response
    except Exception as e:
        logger.error(f'{__name__}: pixivsion error: {repr(e)}')
        response = json_response(data={'error': 'Server error'}, status=500)
        return response
