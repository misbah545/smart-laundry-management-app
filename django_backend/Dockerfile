# Multi-stage build for SmartLaundry Backend

# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 smartlaundry && \
    mkdir -p /var/log/smartlaundry /var/www/smartlaundry/media /var/www/smartlaundry/static && \
    chown -R smartlaundry:smartlaundry /var/log/smartlaundry /var/www/smartlaundry /app

# Copy Python dependencies from builder
COPY --from=builder --chown=smartlaundry:smartlaundry /root/.local /home/smartlaundry/.local

# Copy application code
COPY --chown=smartlaundry:smartlaundry . .

# Set environment
ENV PATH=/home/smartlaundry/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=backend.settings_production

USER smartlaundry

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Expose port
EXPOSE 8000

# Run command
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "backend.asgi:application"]
