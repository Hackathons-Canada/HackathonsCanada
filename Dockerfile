FROM python:3.10-bullseye@sha256:52a58113e1cf1e0987de24226a60aff16cb235068cdbaf4a1a8f9585ae42463b
LABEL org.opencontainers.image.authors="Jason Cameron <jason@jasoncameron.dev>"
#LABEL org.opencontainers.image.source="https://github.com/"
ENV PYTHONUNBUFFERED True
RUN apt-get update && apt-get install -y libpq-dev build-essential
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn  # Install gunicorn

COPY . .

EXPOSE 8080
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "canadahackers:wgsi"]
