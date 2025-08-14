# Dockerfile

FROM python:3.12-slim
WORKDIR /app

ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends gnupg && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8574
CMD ["python3", "-u", "app.py"]

RUN rm -f /tmp/rmeta_session.lock
