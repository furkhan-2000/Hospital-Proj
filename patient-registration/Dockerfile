FROM python:3.11-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:${PATH}" \
    DATABASE_URL=sqlite:////app/data/app.db \
    AUDIT_LOG_FILE=/app/logs/audit.log \
    PATIENT_DATA_DIR=/app/data/patient_data

# Upgrade OS packages, install build deps, then clean up
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user and necessary directories
RUN useradd -m appuser \
    && mkdir -p /app/data /app/logs /app/instance \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app \
    && chmod 700 /app/instance

USER appuser

# Install Python dependencies
COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Expose port and healthcheck
EXPOSE 5003
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5003/api/health || exit 1

# Persist data and logs
VOLUME /app/data /app/logs

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5003", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "60", \
     "--max-requests", "1000", \
     "--max-requests-jitter", "50", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app:create_app()"]
