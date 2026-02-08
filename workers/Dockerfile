FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY workers/requirements.txt /tmp/worker-requirements.txt
COPY backend/requirements.txt /tmp/backend-requirements.txt

# Install dependencies with retry logic
RUN set -eux; \
    for i in 1 2 3; do \
        pip install --no-cache-dir --timeout 120 -r /tmp/worker-requirements.txt && break || { \
            echo "pip install failed, retrying ($i/3)"; \
            sleep 5; \
        }; \
    done && \
    pip install --no-cache-dir --timeout 120 redis tenacity

# Copy application code
COPY workers/processor.py /app/
COPY backend /app/backend/

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/backend

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import redis; redis.from_url('redis://localhost:6379/0').ping()" || exit 1

# Run worker
CMD ["python", "-u", "processor.py"]
