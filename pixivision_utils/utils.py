import aiohttp
import re
from logger import logger
from bs4 import BeautifulSoup


async def fetch_json(url: str, paras: dict = None) -> dict:
    timeout_count = 0
    while timeout_count < 3:
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
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


async def fetch_text(url: str, paras: dict) -> str:
    timeout_count = 0
    while timeout_count < 3:
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                           'accept-language': 'zh-CN,zh;q=0.9'}
                async with session.get(url=url, params=paras, headers=headers, timeout=timeout) as resp:
                    text = await resp.text()
            return text
        except Exception as e:
            logger.info(f'{__name__}: {repr(e)} Occurred in fetch_text trying {timeout_count + 1} using paras: {paras}')
        finally:
            timeout_count += 1
    else:
        logger.error(f'{__name__}: Failed too many times in fetch_text using paras: {paras}')
        return ''


class Pixivsion(object):
    def __init__(self):
        self.__root_url = 'https://www.pixivision.net'
        self.__illustration_url = 'https://www.pixivision.net/zh/c/illustration'
        self.__articles_url = 'https://www.pixivision.net/zh/a'
        self.__tag_url = 'https://www.pixivision.net/zh/t'

    async def get_illustration_list(self) -> dict:
        __html = await fetch_text(url=self.__illustration_url, paras={'lang': 'zh'})
        try:
            __bs = BeautifulSoup(__html, 'lxml')
        except AttributeError:
            return {'error': True}
        __res = {'error': False, 'body': {'illustration': []}}
        __all_illustration_card = __bs.find_all(name='li', attrs={'class': 'article-card-container'})
        for item in __all_illustration_card:
            aid = item.find(name='h2', attrs={'class': 'arc__title'}).find(name='a').attrs['data-gtm-label']
            url = self.__root_url + item.find(name='h2', attrs={'class': 'arc__title'}).find(name='a').attrs['href']
            title = item.find(name='h2', attrs={'class': 'arc__title'}).get_text(strip=True)
            tag_tag = item.find(name='ul', attrs={'class': '_tag-list'}).find_all(name='li')
            tag_list = []
            for tag in tag_tag:
                tag_name = tag.get_text(strip=True)
                tag_r_url = tag.find(name='a').attrs['href']
                tag_id = re.sub(r'^/zh/t/(?=\d+)', '', tag_r_url)
                tag_url = self.__root_url + tag_r_url
                tag_list.append({'tag_id': tag_id, 'tag_name': tag_name, 'tag_url': tag_url})
            __res['body']['illustration'].append({'id': aid, 'title': title, 'url': url, 'tags': tag_list})
        return __res

    async def get_article_info(self, aid: (int, str)) -> dict:
        __url = f'{self.__articles_url}/{aid}'
        __html = await fetch_text(url=__url, paras={'lang': 'zh'})
        try:
            __bs = BeautifulSoup(__html, 'lxml')
        except AttributeError:
            return {'error': True}
        __res = {'error': False, 'body': {'article': {}}}
        article_main = __bs.find(name='div', attrs={'class': '_article-main'})
        article_title = article_main.find(name='h1', attrs={'class': 'am__title'}).get_text(strip=True)
        article_description = article_main.find(name='div',
                                                attrs={'class': 'am__description _medium-editor-text'}).get_text(
            strip=True)
        article_eyecatch_image = article_main.find(name='img', attrs={'class': 'aie__image'}).attrs['src']
        article_body = article_main.find(name='div', attrs={'class': 'am__body'})
        # article_illusts = article_body.find_all(name='div', recursive=False)
        illusts = article_body.find_all(name='div', attrs={'class': 'am__work__main'})
        illusts_list = []
        for item in illusts:
            try:
                url = item.find(name='a', attrs={'class': 'inner-link'}).attrs['href']
                pid = int(re.sub(r'^https://www\.pixiv\.net/artworks/(?=\d+)', '', url))
                image_url = item.find(name='img', attrs={'class': 'am__work__illust'}).attrs['src']
                illusts_list.append({'illusts_id': pid, 'illusts_url': url, 'illusts_image': image_url})
            except Exception as e:
                print(f'Pixivsion get_article_info WARNING: illusts_list class error: {e}')
                continue
        __res['body']['article']['article_title'] = article_title
        __res['body']['article']['article_description'] = article_description
        __res['body']['article']['article_eyecatch_image'] = article_eyecatch_image
        __res['body']['article']['illusts_list'] = illusts_list
        return __res
