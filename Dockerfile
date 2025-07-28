# 🐍 Base image: lightweight Python 3.11
FROM python:3.11-slim

# 📁 Set working directory inside container
WORKDIR /app

# 🐍 Ensure local modules can be imported cleanly
ENV PYTHONPATH=/app

# 🔧 Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔐 Install GnuPG (needed for optional encryption)
RUN apt-get update && apt-get install -y --no-install-recommends gnupg \
  && rm -rf /var/lib/apt/lists/*  # ✅ Clean up APT cache

# 📦 Copy in application code
COPY app.py .
COPY handlers/ handlers/
COPY postprocessors/ postprocessors/
COPY static/ static/
COPY templates/ templates/
COPY keys/ /app/keys/

# 📄 Copy metadata and config files
COPY README.md ./
COPY .env ./

# 🌐 Expose the Flask port
EXPOSE 8574

# 🚀 Start the Flask app
CMD ["python3", "-u", "app.py"]
