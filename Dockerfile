FROM python:3.11.9-slim-bullseye

RUN pip install poetry
WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

COPY . .

ARG GUNICORN_PORT=8080
ENV EXPOSE_PORT=${GUNICORN_PORT}

EXPOSE ${EXPOSE_PORT}

CMD ["python", "-m", "stream_fusion"]