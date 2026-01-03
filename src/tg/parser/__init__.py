from typing import Any
import json
from logger import logger
import asyncio
import random
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from config import settings
import async_requests


async def __parse_data(message: Tag) -> dict[str, Any]:
    message_text = message.select('.tgme_widget_message_text.js-message_text')
    message_id = (
        str(
            message
            .select(
                '.tgme_widget_message.text_not_supported_wrap.js-widget_message',
                limit=1
            )[0]
            .get('data-post')
        ).replace(f'{settings.telegram.channel_name}/', ''))
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
        'id': int(message_id),
        'text': message_text[0].getText(),
        'image_urls': image_urls,
    }


async def parse_messages(after: int | None = None, before: int | None = None) -> list[dict[str, Any]] | None:
    '''
    Парсинг 15 сообщений

    Args:
        after (int, optional): ID поста, после которого будут спаршены сообщения. По-умолчанию: None.
        before (int, optional): ID поста, до которого будут спаршены сообщения. По-умолчанию: None.

    Returns:
        list[dict[str,Any]]: Спаршенные сообщения в формате 
    ```
    [
        {
            "id": message_id,
            "text": message_text,
            "image_urls": [image_urls]
        }
    ]
        ```
    '''
    if before is not None and after is not None:
        raise ValueError('Нельзя одновременно использовать before и after')

    base_url = f'https://t.me/s/{settings.telegram.channel_name}'

    if after is not None:
        url = f'{base_url}?after={after}'
    elif before is not None:
        url = f'{base_url}?before={before}'
    else:
        url = base_url

    try:
        response = await async_requests.get(url)
    except Exception as e:
        raise e
    else:
        soup = bs(response.text, 'html.parser')
        messages = soup.select('.tgme_widget_message_wrap.js-widget_message_wrap')
        parsed_data = [await __parse_data(m) for m in messages]
        return parsed_data


async def parse_messages_all() -> list[dict[str, Any]]:
    '''
    Парсинг всех сообщений из канала

    Raises:
        Exception: Не удалось спарсить сообщения

    Returns:
        list[dict[str,Any]]: Спаршенные сообщения в формате 
    ```
    [
        {
            "id": message_id,
            "text": message_text,
            "image_urls": [image_urls]
        }
    ]
    ```
    '''
    result = []
    parsed = await parse_messages(before=0)
    if parsed is None:
        raise Exception('Не удалось спарсить сообщения')
    last_msg_id = parsed[-1]['id'] + 10  # 10 с запасом на изображения, которые считаются за отдельные сообщения
    msg_id = 0
    count = 1

    while msg_id < last_msg_id:
        parsed = await parse_messages(after=count)
        if parsed is not None:
            count += len(parsed)
            for m in parsed:
                result.append(m)
                # logger.info(json.dumps(m, ensure_ascii=False, indent=2))
        await asyncio.sleep(random.randint(2, 5))
    return result
