FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="$PATH:/opt/poetry/bin"

RUN apk add --no-cache \
        openssl \
        postgresql-client \
        gcc \
        musl-dev \
        libffi-dev \
    && pip install --no-cache-dir "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

ARG GUNICORN_PORT=8080
ENV EXPOSE_PORT=${GUNICORN_PORT}
EXPOSE ${EXPOSE_PORT}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "-m", "stream_fusion"]