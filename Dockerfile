FROM python:3.12-slim         as builder
LABEL org.opencontainers.image.authors="Jason Cameron <jason@jasoncameron.dev>"
LABEL org.opencontainers.image.source="https://github.com/Hackathons-Canada/HackathonsCanada"
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.3

RUN apt-get update \
  && apt-get install  --no-install-suggests --no-install-recommends -y build-essential libpq-dev gettext pipx \
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*
ENV PATH="/root/.local/bin:${PATH}"
RUN pipx install poetry
RUN pipx inject poetry poetry-plugin-bundle
WORKDIR /src
COPY . .
COPY poetry.lock pyproject.toml ./

RUN poetry bundle venv --python=/usr/bin/python3 --with prod /venv

FROM python:3.12-slim
COPY --from=builder /venv /venv

COPY ./scripts /scripts

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
