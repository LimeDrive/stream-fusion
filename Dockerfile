FROM python:3.12-alpine AS builder

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$PATH:/opt/poetry/bin"

RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt --only main --without-hashes \
    && pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine AS development

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

RUN apk add --no-cache \
        gcc \
        musl-dev \
        libffi-dev \
        openssl \
        openssh \
        postgresql-client \
        git \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --with dev

ARG GUNICORN_PORT=8080
ENV EXPOSE_PORT=${GUNICORN_PORT}
EXPOSE ${EXPOSE_PORT}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/bin/sh"]

FROM python:3.12-alpine AS production

ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
        openssl \
        postgresql-client

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . .

ARG GUNICORN_PORT=8080
ENV EXPOSE_PORT=${GUNICORN_PORT}
EXPOSE ${EXPOSE_PORT}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]