import re
import os
from config import API_KEY
from logger import logger
from aiohttp.web_request import Request
from aiohttp.web import json_response, FileResponse
from .utils import search_gallery_by_tag, download_gallery


async def nhentai_search(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'tag']:
            return json_response(data={'error': True, 'body': 'Illegal parameters'}, status=403)
    key = data.get('key')
    if key not in API_KEY:
        return json_response(data={'error': True, 'body': 'Unauthorized access'}, status=403)
    tag = data.get('tag')
    if not tag:
        return json_response(data={'error': True, 'body': 'Missing parameters'}, status=400)

    res = await search_gallery_by_tag(tag=tag)

    if tag:
        response = json_response(data={'error': False, 'body': res}, status=200)
    else:
        response = json_response(data={'error': True, 'body': 'Not found'}, status=503)

    return response


async def nhentai_download(request: Request):
    data = request.query
    for param in data.keys():
        if param not in ['key', 'id']:
            return json_response(data={'error': True, 'body': 'Illegal parameters'}, status=403)
    key = data.get('key')
    if key not in API_KEY:
        return json_response(data={'error': True, 'body': 'Unauthorized access'}, status=403)
    _id = data.get('id')
    if not _id:
        return json_response(data={'error': True, 'body': 'Missing parameters'}, status=400)
    elif re.match(r'^\d+$', _id):
        success, password = await download_gallery(int(_id))
        if success:
            return json_response(data={'error': False, 'body': {'password': password, 'gallery_id': _id}}, status=200)
        else:
            return json_response(data={'error': True, 'body': 'Download failed'}, status=503)
    else:
        return json_response(data={'error': True, 'body': 'Missing or illegal parameters'}, status=400)


async def nhentai_get(request: Request):
    sub_dir = os.path.join(os.path.dirname(__file__), 'nhentai_gallery')
    null = os.path.join(sub_dir, 'null')

    data = request.query
    for param in data.keys():
        if param not in ['key', 'id']:
            return FileResponse(path=null, status=403, reason='Illegal parameters')
    key = data.get('key')
    if key not in API_KEY:
        return FileResponse(path=null, status=403, reason='Unauthorized access')
    _id = data.get('id')
    if not _id:
        return FileResponse(path=null, status=400, reason='Missing parameters')
    elif re.match(r'^\d+$', _id):
        file = os.path.join(sub_dir, _id, f'{_id}.7z')

        if os.path.exists(file):
            headers = {'Content-Disposition': f'attachment;filename={_id}.7z'}
            return FileResponse(path=file, status=200, headers=headers)
        else:
            return FileResponse(path=null, status=503, reason='Not found')
    else:
        return FileResponse(path=null, status=400, reason='Missing or illegal parameters')
