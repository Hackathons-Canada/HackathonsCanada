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

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn psycopg2-binary # Install prod-specific dependencies

COPY . .


RUN mv ./scripts /scripts

RUN sed -i 's/\r$//g' /scripts/django/start
RUN sed -i 's/\r$//g' /scripts/celery/worker/start
RUN sed -i 's/\r$//g' /scripts/celery/beat/start
RUN sed -i 's/\r$//g' /scripts/flower/start
RUN sed -i 's/\r$//g' /scripts/entrypoint.sh

RUN chmod +x /scripts/django/start
RUN chmod +x /scripts/celery/worker/start
RUN chmod +x /scripts/celery/beat/start
RUN chmod +x /scripts/flower/start
RUN chmod +x /scripts/entrypoint.sh

ENTRYPOINT ["/scripts/entrypoint.sh"]