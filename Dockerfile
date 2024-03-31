FROM python:3.10-slim
LABEL org.opencontainers.image.authors="Jason Cameron <jason@jasoncameron.dev>"
#LABEL org.opencontainers.image.source="https://github.com/"
ENV PYTHONUNBUFFERED True
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn  # Install gunicorn

COPY . .

EXPOSE 8080
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "canadahackers:wgsi"]
