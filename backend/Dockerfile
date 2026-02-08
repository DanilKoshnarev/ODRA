FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
# Retry pip install up to 3 times to mitigate transient network/read timeouts
RUN set -eux; \
    for i in 1 2 3; do \
        pip install --no-cache-dir --timeout 120 -r requirements.txt && break || { \
            echo "pip install failed, retrying ($i/3)"; \
            sleep 5; \
        }; \
    done

# Copy app
COPY app/ app/

# Expose port
EXPOSE 8000

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
