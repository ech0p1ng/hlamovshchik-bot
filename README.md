# hlamovshchik-bot

## Что это?
---

Телеграм-бот для поиска изображений по текстовому описанию.

## Как это работает?
---
Бот берет посты из *публичного* телеграм-канала, считывает текст из поста и сопоставляет его с изображениями в посте. Идеально подходит для мгновенного поиска изображений на случай важных переговоров.

## Как это использовать?
---
Достаточно зайти в переписку с ботом и использовать команды:

`/start` - Обычное приветствие
`/find` - Поиск по изображений по тексту
`/parse` - Парсинг постов в базу бота. Только для администраторов бота.

А также можно использовать в **абсолютно любом чате**! Просто введите в поле ввода сообщения `@ваш_bot здарова, давно не виделись`, и бот выдаст все изображения, в постах с которыми встречается текст `здарова, давно не виделись`. Это называется `Inline mode`.

## Как это запустить?
---
0. Для начала вам нужен сервер минимум с 10Гб свободного места на диске и 2Гб ОЗУ.

1. Создайте своего бота через официального бота для создания своих ботов в телеграм `@BotFather` и получите токен.

2. Включите Inline mode, введя команду `/setinline` и выберите вашего бота.

3. Скопируйте репозиторий на свой сервер.

4. В корне проекта создайте `.env` файл со следующим содержимым:
```
TELEGRAM__BOT_TOKEN=0000000000:ABcdEFghIJklM-NopQRstUVwxYZabC_DefG
TELEGRAM__CHANNEL_ID=0000000000
TELEGRAM__CHANNEL_NAME=channelname
TELEGRAM__CHAT_ID=000000000

POSTGRES__HOST=postgres_db
POSTGRES__PORT=5432
POSTGRES__DB=postgres
POSTGRES__USER=postgres
POSTGRES__PASSWORD=postgres
POSTGRES__VERSION=18
POSTGRES__DUMP_TIMEOUT_SECONDS=7200

MINIO__ROOT_USER=minio
MINIO__ROOT_PASSWORD=minio
MINIO__ACCESS_KEY=minio
MINIO__SECRET_KEY=minio
MINIO__BUCKET_NAME=private-bucket
MINIO__PORT=9000
MINIO__PORT_SECURE=9001
MINIO__ENDPOINT=minio:${MINIO__PORT}
MINIO__ENDPOINT_SECURE=minio:${MINIO__PORT_SECURE}
MINIO__IP=255.255.255.255
MINIO__DOMAIN=example.com
MINIO__ADMIN_DOMAIN=admin.${MINIO__DOMAIN}

ATTACHMENT__MAX_SIZE=20971520
ATTACHMENT__EXTENSIONS=["webp", "jpg", "jpeg", "png", "gif", "mp4", "avi", "webm"]
ATTACHMENT__VIDEO_EXTENSIONS=["gif", "mp4", "avi", "webm"]
ATTACHMENT__IMAGE_EXTENSIONS=["webp", "jpg", "jpeg", "png"]

POETRY_VERSION=2.2.1
```

**!!! Значения всех переменных, имена которых содержат слова `ID`, `NAME`, `USER`, `PASSWORD`, `KEY`, `TOKEN`, `IP`, `DOMAIN` необходимо заменить на свои !!!** 

**!! Для работы `Inline mode` бот должен быть запущен на сервере, получившем не самоподписанные TLS-сертификаты !!**

5. Установите `Docker` и `Docker Compose` на ваш сервер

6. Перейдите в каталог проекта (в ней должен находиться файл `docker-compose.yml`)

7. Введите следующую команду
```bash
docker-compose up --build
```
или 
```bash
docker compose up --build
```
в зависимости от версии Docker

8. (Не обязательно) Если хотите запустить только бота, не включая базы данных

Linux:
```bash
python3 -m pip install --upgrade pip
python3 -m venv .venv
.venv/scripts/activate
pip install poetry
poetry install --no-root
```

Windows:

```cmd
python -m pip install --upgrade pip
python -m venv .venv
.venv/Scripts/activate
pip install poetry
poetry install --no-root
```

## Всё! Можете пользоваться ботом!