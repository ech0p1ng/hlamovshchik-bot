from typing import Any
from bs4 import BeautifulSoup as bs
from bs4 import Tag
import httpx
import config
import asyncio
import json


async def __fetch(url: str) -> httpx.Response:
    '''
    GET-запрос

    Args:
        url (str): URL

    Raises:
        Exception: Не удалось загрузить страинцу

    Returns:
        httpx.Response: Ответ сервера
    '''

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0',
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(
                f'Не удалось загрузить страинцу: {response.status_code}'
            )
        return response


async def __parse_data(message: Tag) -> dict[str, Any]:
    message_text = message.select('.tgme_widget_message_text.js-message_text')
    message_id = (str(message
                  .select('.tgme_widget_message.text_not_supported_wrap.js-widget_message')[0]
                  .get('data-post'))
                  .replace(f'{config.CHANNEL_NAME}/', ''))
    media = message.select('a.tgme_widget_message_photo_wrap')
    image_urls = []
    for m in media:
        style_attr = m.get('style')
        styles = str(style_attr).split(';')
        for s in styles:
            if s.startswith('background-image:url('):
                url = s.replace("background-image:url('", '')[:-2]
                image_urls.append(url)
    return {
        'id': message_id,
        'text': message_text[0].getText(),
        'image_urls': image_urls,
    }


async def parse_messages(after: int = 1) -> list[dict[str, Any]]:
    url = f'https://t.me/s/{config.CHANNEL_NAME}?after={after}'
    response = await __fetch(url)
    soup = bs(response.text, 'html.parser')
    messages = soup.select('.tgme_widget_message_wrap.js-widget_message_wrap')
    parsed_data = [await __parse_data(m) for m in messages]
    return parsed_data
    # with open(f'messages{after}.json', 'w', encoding='utf8') as f:
    #     f.write(json.dumps(parsed_data, ensure_ascii=False, indent=2))
