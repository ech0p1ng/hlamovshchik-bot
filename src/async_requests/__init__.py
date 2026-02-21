from io import BytesIO
from typing import Any
import httpx
import asyncio


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


async def get(url: str, max_retries: int = 10, delay_seconds: int = 5) -> httpx.Response:
    '''
    Асинхронный GET-запрос

    Args:
        url (str): URL
        max_retries (int, optional): Максимальное количество попыток. По умолчанию: `10`.
        delay_seconds (int, optional): Время ожидания после неудачной попытки. По умолчанию: `5`.

    Raises:
        httpx.HTTPError: Не удалось загрузить

    Returns:
        httpx.Response: Ответ сервера
    '''
    msg = f'Не удалось загрузить {url}: Неизвестная ошибка'
    async with httpx.AsyncClient() as client:
        for retry in range(1, max_retries + 1):
            response = await client.get(url, headers=REQUEST_HEADERS)
            
            if response.status_code == 502:
                await asyncio.sleep(delay_seconds * 2 ** (retry - 1))
                continue
            
            if response.status_code == 200:
                return response
            
            msg = f'Не удалось загрузить {url}: {response.status_code}'
    
    raise httpx.HTTPError(msg)


async def download_file(url: str) -> dict[str, Any]:
    '''
    Скачать файл из `url`

    Args:
        url (str): URL медиа-файла

    Returns:
        dict[str,Any]: Загруженный файл его имя и расширение
    ```
    {
        "file": file,
        "name": file_name,
        "ext": file_ext
    }
    ```

    Raises:
        httpx.HTTPError: Не удалось загрузить `url`: `status_code`
    '''
    full_file_name = url.split('/')[-1]
    file_ext = full_file_name.split('.')[-1]
    file_name = full_file_name.replace('.' + file_ext, '')
    response = await get(url)
    file = BytesIO(response.content)
    return {
        'file': file,
        'name': file_name,
        'ext': file_ext
    }
