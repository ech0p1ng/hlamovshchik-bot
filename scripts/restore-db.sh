#!/bin/bash
set -e

# Путь к файлу дампа — обязательный аргумент
DUMP_FILE="$1"

if [ -z "$DUMP_FILE" ]; then
  echo "❌ Использование: $0 <путь_к_файлу_дампа.sql>"
  exit 1
fi

if [ ! -f "$DUMP_FILE" ]; then
  echo "❌ Файл дампа не найден: $DUMP_FILE"
  exit 1
fi

# Загружаем переменные из .env (если нужно)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Параметры подключения (можно переопределить через env)
DB_HOST=${POSTGRES__HOST:-db}
DB_PORT=${POSTGRES__PORT:-5432}
DB_NAME=${POSTGRES__DB:-myapp}
DB_USER=${POSTGRES__USER:-postgres}
DB_PASSWORD=${POSTGRES__PASSWORD:-password}

echo "🔄 Восстановление БД '$DB_NAME' из файла: $DUMP_FILE"
echo "   Хост: $DB_HOST, Порт: $DB_PORT, Пользователь: $DB_USER"

# Экспортируем пароль для psql (чтобы не спрашивал)
export PGPASSWORD="$DB_PASSWORD"

# Восстанавливаем через psql
psql \
  --host="$DB_HOST" \
  --port="$DB_PORT" \
  --username="$DB_USER" \
  --dbname="$DB_NAME" \
  --file="$DUMP_FILE" \
  --quiet

echo "✅ Восстановление завершено успешно!"