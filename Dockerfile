FROM python:3.10-slim
LABEL org.opencontainers.image.authors="Jason Cameron <jason@jasoncameron.dev>"
#LABEL org.opencontainers.image.source="https://github.com/"
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn  # Install gunicorn

COPY . .

EXPOSE 8080
ENTRYPOINT ./entrypoint.sh
