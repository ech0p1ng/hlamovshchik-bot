#!/bin/sh
set -e

echo "$(date): Проверка необходимости обновления сертификатов..."
if certbot renew --webroot -w /var/www/certbot ; then
    echo "$(date): Сертификаты обновлены. Перезагружаем nginx..."
    # Отправляем сигнал перезагрузки в контейнер nginx
    kill -HUP $(cat /var/run/nginx.pid)
else
    echo "$(date): Обновление не требуется."
fi