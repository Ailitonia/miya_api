import aiohttp
import re
import base64
import random
from io import BytesIO
from logger import logger


illust_data_url = 'https://www.pixiv.net/ajax/illust/'
illust_artwork_url = 'https://www.pixiv.net/artworks/'
ranking_url = 'http://www.pixiv.net/ranking.php'


async def fetch_json(url: str, paras: dict = None) -> dict:
    timeout_count = 0
    while timeout_count < 3:
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                           'referer': 'https://www.pixiv.net/',
                           'accept-language': 'zh-CN,zh;q=0.9'}
                async with session.get(url=url, params=paras, headers=headers, timeout=timeout) as resp:
                    _json = await resp.json()
            return _json
        except Exception as e:
            logger.info(f'{__name__}: {repr(e)} Occurred in fetch_json trying {timeout_count + 1} using paras: {paras}')
        finally:
            timeout_count += 1
    else:
        logger.error(f'{__name__}: Failed too many times in fetch_json using paras: {paras}')
        return {}


# 获取作品完整信息（pixiv api 获取 json）
# 返回格式化后的作品信息
async def get_illust_data(illust_id: [str, int]) -> dict:
    illust_url = illust_data_url + str(illust_id)
    result = await fetch_json(url=illust_url)
    if result.get('error'):
        logger.warning(f'{__name__}: Get_illust_data, failed to fetch illust info.')
        return {'error': True, 'body': {}}
    try:
        # 处理作品基本信息
        illustid = int(result['body']['illustId'])
        illusttitle = str(result['body']['illustTitle'])
        userid = int(result['body']['userId'])
        username = str(result['body']['userName'])
        url = illust_artwork_url + str(illust_id)
        illust_orig_url = str(result['body']['urls']['original'])
        illust_regular_url = str(result['body']['urls']['regular'])
        illust_description = str(result['body']['description'])
        re_std_description_s1 = r'(\<br\>|\<br \/\>)'
        re_std_description_s2 = r'<[^>]+>'
        illust_description = re.sub(re_std_description_s1, '\n', illust_description)
        illust_description = re.sub(re_std_description_s2, '', illust_description)
        # 处理作品tag
        illusttag = []
        tag_number = len(result['body']['tags']['tags'])
        for num in range(tag_number):
            tag = str(result['body']['tags']['tags'][num]['tag'])
            illusttag.append(tag)
            try:
                transl_tag = str(result['body']['tags']['tags'][num]['translation']['en'])
                illusttag.append(transl_tag)
            except Exception as e:
                logger.debug(f'{__name__}: Get_illust_data, tag not has translation, {repr(e)}, ignored')
                continue
        if 'R-18' in illusttag:
            is_r18 = True
        else:
            is_r18 = False
        __resDict = {'pid': illustid, 'title': illusttitle, 'uid': userid, 'uname': username,
                     'url': url, 'orig_url': illust_orig_url, 'regular_url': illust_regular_url,
                     'description': illust_description, 'tags': illusttag, 'is_r18': is_r18}
        __res = {'error': False, 'body': __resDict}
    except Exception as e:
        __res = {'error': True, 'body': {'errinfo': repr(e)}}
    return __res


# 图片转base64
async def pic_2_base64(url: str) -> str:
    async def fetch_image(_url: str, paras: dict = None) -> bytes:
        timeout_count = 0
        while timeout_count < 3:
            try:
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                               'referer': 'https://www.pixiv.net/',
                               'accept-language': 'zh-CN,zh;q=0.9'}
                    async with session.get(url=url, params=paras, headers=headers, timeout=timeout) as resp:
                        image = await resp.read()
                return image
            except Exception as _e:
                logger.info(
                    f'{__name__}: {repr(_e)} Occurred in fetch_image trying {timeout_count + 1} using paras: {paras}')
            finally:
                timeout_count += 1
        else:
            logger.error(f'{__name__}: Failed too many times in fetch_image using paras: {paras}')
            return bytes()

    origin_image_f = BytesIO()
    try:
        origin_image_f.write(await fetch_image(_url=url))
    except Exception as e:
        logger.error(f'{__name__}: Pic_2_base64 error: {repr(e)}')
        return ''
    b64 = base64.b64encode(origin_image_f.getvalue())
    b64 = str(b64, encoding='utf-8')
    b64 = 'base64://' + b64
    origin_image_f.close()
    return b64


async def rand_daily_ranking(num: int) -> dict:
    payload_daily = {'format': 'json', 'mode': 'daily',
                     'content': 'illust', 'p': 1}
    illust_list = await fetch_json(url=ranking_url, paras=payload_daily)
    result = []
    try:
        rand_illust_num = random.sample(range(len(illust_list['contents'])), k=num)
        for num in rand_illust_num:
            illust_id = illust_list['contents'][num]['illust_id']
            result.append(illust_id)
    except Exception as e:
        logger.error(f'{__name__}: Failed too get_rand_daily_ranking: {repr(e)}')
        return {'error': True, 'body': result}
    return {'error': False, 'body': result}


async def rand_weekly_ranking(num: int) -> dict:
    payload_daily = {'format': 'json', 'mode': 'weekly',
                     'content': 'illust', 'p': 1}
    illust_list = await fetch_json(url=ranking_url, paras=payload_daily)
    result = []
    try:
        rand_illust_num = random.sample(range(len(illust_list['contents'])), k=num)
        for num in rand_illust_num:
            illust_id = illust_list['contents'][num]['illust_id']
            result.append(illust_id)
    except Exception as e:
        logger.error(f'{__name__}: Failed too get_rand_daily_ranking: {repr(e)}')
        return {'error': True, 'body': result}
    return {'error': False, 'body': result}


async def rand_monthly_ranking(num: int) -> dict:
    payload_daily = {'format': 'json', 'mode': 'monthly',
                     'content': 'illust', 'p': 1}
    illust_list = await fetch_json(url=ranking_url, paras=payload_daily)
    result = []
    try:
        rand_illust_num = random.sample(range(len(illust_list['contents'])), k=num)
        for num in rand_illust_num:
            illust_id = illust_list['contents'][num]['illust_id']
            result.append(illust_id)
    except Exception as e:
        logger.error(f'{__name__}: Failed too get_rand_daily_ranking: {repr(e)}')
        return {'error': True, 'body': result}
    return {'error': False, 'body': result}


if __name__ == '__main__':
    # Testing
    import asyncio
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(get_illust_data(79168467))
    r2 = loop.run_until_complete(rand_monthly_ranking(2))
    print(r2)
