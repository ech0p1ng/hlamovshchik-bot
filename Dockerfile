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
RUN chmod +x /app/scripts/init-letsencrypt.sh
RUN chmod +x /app/scripts/renew-certs.sh

FROM base AS server

ENV PYTHONPATH=/app/src

RUN chmod +x /app/scripts/entrypoint.sh

RUN poetry lock

RUN poetry install --no-root

ENTRYPOINT ["/app/scripts/entrypoint.sh"]


FROM base AS dev

ENV PYTHONPATH=/app/src

RUN chmod +x /app/scripts/entrypoint-dev.sh

ENTRYPOINT ["/app/scripts/entrypoint-dev.sh"]


FROM base AS devfast

ENV PYTHONPATH=/app/src

RUN chmod +x /app/scripts/entrypoint-devfast.sh

RUN poetry lock

RUN poetry install --no-root

ENTRYPOINT ["/app/scripts/entrypoint-devfast.sh"]