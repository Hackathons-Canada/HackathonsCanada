FROM python:3.12-slim
LABEL org.opencontainers.image.authors="Jason Cameron <jason@jasoncameron.dev>"
LABEL org.opencontainers.image.source="https://github.com/Hackathons-Canada/HackathonsCanada"
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Additional dependencies
  && apt-get install -y git \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 -


WORKDIR /app
COPY poetry.lock pyproject.toml ./

RUN poetry install --no-root --with prod

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
