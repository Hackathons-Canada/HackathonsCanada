FROM python:3.12-slim-bullseye as builder
LABEL org.opencontainers.image.authors="Jason Cameron <jason@jasoncameron.dev>"
LABEL org.opencontainers.image.source="https://github.com/Hackathons-Canada/HackathonsCanada"
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONUNBUFFERED=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=True \
  POETRY_CACHE_DIR='/tmp/pypoetry'

RUN apt-get update \
  && apt-get install --no-install-suggests --no-install-recommends -y build-essential libpq-dev gettext \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/* \

RUN pip install poetry

WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN python -m poetry install --with prod --no-root

FROM python:3.12-slim-bullseye

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /app
COPY . .
RUN mv ./scripts /scripts

RUN sed -i 's/\r$//g' /scripts/django/start &&  \
    sed -i 's/\r$//g' /scripts/celery/worker/start &&  \
    sed -i 's/\r$//g' /scripts/celery/beat/start &&  \
    sed -i 's/\r$//g' /scripts/flower/start &&  \
    sed -i 's/\r$//g' /scripts/entrypoint.sh

RUN chmod +x /scripts/django/start && \
    chmod +x /scripts/celery/worker/start &&  \
    chmod +x /scripts/celery/beat/start && \
    chmod +x /scripts/flower/start && \
    chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]
