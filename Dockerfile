FROM python:3.12-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

ENV PYTHONPATH=/app
ENV DATABASE_URL=""
ENV REDIS_URL=""
ENV SECRET_KEY=""
ENV DEBUG=False

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; import os; port = os.getenv('PORT', '8000'); requests.get(f'http://localhost:{port}/health', timeout=5)" || exit 1

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]