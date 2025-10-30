FROM python:3.11-slim

WORKDIR /app

# kadang lib lain perlu gcc, kita siapin minimal
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# default env
ENV FLASK_ENV=production
# Render bakal kasih PORT, tapi kita kasih fallback biar bisa jalan lokal juga
ENV PORT=5000

# Gunicorn = production server
CMD exec gunicorn --bind 0.0.0.0:$PORT app:app
