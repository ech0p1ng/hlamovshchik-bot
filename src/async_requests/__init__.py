import httpx
from config import settings


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


async def get(url: str) -> httpx.Response:
    '''
    Асинхронный GET-запрос

    Args:
        url (str): URL

    Raises:
        httpx.HTTPError: Не удалось загрузить

    Returns:
        httpx.Response: Ответ сервера
    '''

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=REQUEST_HEADERS)
        if response.status_code != 200:
            msg = f'Не удалось загрузить {url}: {response.status_code}'
            raise httpx.HTTPError(msg)
        return response
