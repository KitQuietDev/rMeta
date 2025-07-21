FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y gnupg
COPY app.py .
COPY handlers/ handlers/
COPY postprocessors/ postprocessors/
COPY static/ /app/static/
COPY . .

EXPOSE 8574

CMD ["python", "app.py"]
