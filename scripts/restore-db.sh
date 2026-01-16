#!/bin/bash
set -e

# Путь к файлу дампа — обязательный аргумент
DUMP_FILE="$1"

docker exec -i postgres_db psql -U ${POSTGRES__USER} -d ${POSTGRES__DB} < $DUMP_FILE