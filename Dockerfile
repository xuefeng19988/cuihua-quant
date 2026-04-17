# Dockerfile for Cuihua Quant System
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install optional dependencies
RUN pip install --no-cache-dir \
    flask \
    gunicorn \
    lightgbm \
    scikit-learn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data/logs models

# Expose ports
# 5000 for web dashboard
# 11112 for Futu OpenD (if running in same container)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/status')" || exit 1

# Default command
CMD ["python", "src/web/dashboard.py"]
