FROM python:3.13-slim AS base

ARG POETRY_VERSION

WORKDIR /app



ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN mkdir -p /root/.cache/pypoetry/virtualenvs && \
    touch /root/.cache/pypoetry/virtualenvs/envs.toml

RUN pip install --upgrade pip
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

RUN poetry env use /usr/local/bin/python

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-root --no-ansi

COPY src/ /app/src
COPY alembic/ /app/alembic
COPY scripts/ /app/scripts

ENV PYTHONPATH=/app/src


FROM base AS server

RUN chmod +x /app/scripts/entrypoint.sh

ENTRYPOINT ["/app/scripts/entrypoint.sh"]


FROM base AS dev

RUN chmod +x /app/scripts/entrypoint-dev.sh

ENTRYPOINT ["/app/scripts/entrypoint-dev.sh"]