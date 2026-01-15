#!/bin/sh
set -e

# Загружаем .env
export $(grep -v '^#' .env | xargs)

# Генерируем nginx.conf из шаблона
envsubst < nginx/templates/nginx.conf.template > nginx/nginx.conf

# Запускаем временный Nginx для прохождения проверки
docker compose up -d nginx

# Ждём, пока поднимется
sleep 5

# Получаем сертификат
docker compose run --rm certbot

# Перезапускаем Nginx с HTTPS
docker compose restart nginx