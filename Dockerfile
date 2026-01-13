FROM python:3.13 AS base

ARG POETRY_VERSION

WORKDIR /app

COPY . .

ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

    RUN mkdir -p /root/.cache/pypoetry/virtualenvs && \
    touch /root/.cache/pypoetry/virtualenvs/envs.toml
RUN pip install --upgrade pip
RUN pip install poetry==${POETRY_VERSION}
RUN poetry env use /usr/local/bin/python


FROM base AS server

ENV PYTHONPATH=/app/src

RUN chmod +x /app/entrypoint.sh

RUN poetry lock

RUN poetry install --no-root

ENTRYPOINT ["/app/entrypoint.sh"]


FROM base AS dev

ENV PYTHONPATH=/app/src

RUN chmod +x /app/entrypoint-dev.sh

ENTRYPOINT ["/app/entrypoint-dev.sh"]


FROM base AS devfast

ENV PYTHONPATH=/app/src

RUN chmod +x /app/entrypoint-devfast.sh

RUN poetry lock

RUN poetry install --no-root

ENTRYPOINT ["/app/entrypoint-devfast.sh"]