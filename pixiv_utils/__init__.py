import re
from config import API_KEY
from logger import logger
from aiohttp.web_request import Request
from aiohttp.web import json_response
from .utils import get_illust_data, rand_daily_ranking, rand_weekly_ranking, rand_monthly_ranking, pic_2_base64


async def pixiv_illust(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'pid']:
            response = json_response(data={'error': 'Illegal parameters'}, status=403)
            return response
    key = data.get('key')
    if key not in API_KEY:
        response = json_response(data={'error': 'Unauthorized access'}, status=403)
        return response
    illust_id = data.get('pid')
    if not illust_id:
        response = json_response(data={'error': 'Missing parameters'}, status=400)
        return response
    if re.match(r'^\d+$', illust_id):
        try:
            illust_data = await get_illust_data(illust_id=illust_id)
            if not illust_data.get('error'):
                _res = illust_data.get('body')
                response = json_response(data=_res, status=200)
                return response
            else:
                response = json_response(data={'error': 'Can not get illust info'}, status=500)
                return response
        except Exception as e:
            logger.error(f'{__name__}: pixiv_illust error: {repr(e)}')
            response = json_response(data={'error': 'Server error'}, status=500)
            return response
    else:
        response = json_response(data={'error': 'Missing or illegal parameters'}, status=400)
        return response


async def pixiv_illust_withb64(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'pid', 'mode']:
            response = json_response(data={'error': 'Illegal parameters'}, status=403)
            return response
    key = data.get('key')
    if key not in API_KEY:
        response = json_response(data={'error': 'Unauthorized access'}, status=403)
        return response
    mode = data.get('mode')
    if mode not in ['origin', 'regular']:
        response = json_response(data={'error': 'Illegal parameters'}, status=403)
        return response
    illust_id = data.get('pid')
    if not illust_id:
        response = json_response(data={'error': 'Missing parameters'}, status=400)
        return response
    if re.match(r'^\d+$', illust_id):
        try:
            illust_data = await get_illust_data(illust_id=illust_id)
            if not illust_data.get('error'):
                _res = illust_data.get('body')
                if mode == 'origin':
                    url = _res.get('orig_url')
                    image_b64 = await pic_2_base64(url=url)
                    _res.update(pic_b64=image_b64)
                else:
                    url = _res.get('regular_url')
                    image_b64 = await pic_2_base64(url=url)
                    _res.update(pic_b64=image_b64)
                response = json_response(data=_res, status=200)
                return response
            else:
                response = json_response(data={'error': 'Can not get illust info'}, status=500)
                return response
        except Exception as e:
            logger.error(f'{__name__}: pixiv_illust_withb64 error: {repr(e)}')
            response = json_response(data={'error': 'Server error'}, status=500)
            return response
    else:
        response = json_response(data={'error': 'Missing or illegal parameters'}, status=400)
        return response


async def pixiv_rank(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'num', 'mode']:
            response = json_response(data={'error': 'Illegal parameters'}, status=403)
            return response
    key = data.get('key')
    if key not in API_KEY:
        response = json_response(data={'error': 'Unauthorized access'}, status=403)
        return response
    mode = data.get('mode')
    if mode not in ['daily', 'weekly', 'monthly']:
        response = json_response(data={'error': 'Illegal parameters'}, status=403)
        return response
    try:
        num = data.get('num')
        if not num:
            response = json_response(data={'error': 'Missing parameters'}, status=400)
            return response
        if re.match(r'^\d+$', num):
            num = int(num)
            if mode == 'daily':
                _res = await rand_daily_ranking(num)
                if not _res.get('error'):
                    response = json_response(data=_res, status=200)
                else:
                    response = json_response(data={'error': 'Can not get rank info'}, status=500)
                return response
            elif mode == 'weekly':
                _res = await rand_weekly_ranking(num)
                if not _res.get('error'):
                    response = json_response(data=_res, status=200)
                else:
                    response = json_response(data={'error': 'Can not get rank info'}, status=500)
                return response
            elif mode == 'monthly':
                _res = await rand_monthly_ranking(num)
                if not _res.get('error'):
                    response = json_response(data=_res, status=200)
                else:
                    response = json_response(data={'error': 'Can not get rank info'}, status=500)
                return response
            else:
                response = json_response(data={'error': 'Missing or illegal parameters'}, status=400)
                return response
        else:
            response = json_response(data={'error': 'illegal parameters'}, status=400)
            return response
    except Exception as e:
        logger.error(f'{__name__}: pixivsion error: {repr(e)}')
        response = json_response(data={'error': 'Server error'}, status=500)
        return response
