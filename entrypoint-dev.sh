#!/bin/bash
poetry install --no-root
poetry run alembic upgrade head
# poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
poetry run watchfiles --filter python "poetry run python -m debugpy --listen 0.0.0.0:5678 --wait-for-client src/main.py" src/