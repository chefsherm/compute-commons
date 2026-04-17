FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Cloud Run injects PORT env var — default 8080
ENV PORT=8080

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

EXPOSE ${PORT}

# Production: no --reload, workers=1 for Cloud Run (scale via instances)
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 1
