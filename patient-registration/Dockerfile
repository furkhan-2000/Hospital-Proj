FROM python:3.11-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    PATH="/home/appuser/.local/bin:${PATH}" \
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

# Create non-root user and dirs
RUN useradd -m appuser \
    && mkdir -p /app/data /app/logs /app/instance /home/appuser/.local/bin \
    && chown -R appuser:appuser /app /home/appuser \
    && chmod -R 755 /app \
    && chmod 700 /app/instance

# Install Python dependencies as root
COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Switch to non-root
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Ensure uploads exists if used
RUN mkdir -p /app/uploads

# Run asset download
RUN chmod +x download_assets.sh && ./download_assets.sh

# Expose and healthcheck
EXPOSE 5003
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5003/api/health || exit 1

# Persist data and logs
VOLUME /app/data /app/logs /app/uploads

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5003",
     "--workers", "2",
     "--threads", "4",
     "--timeout", "60",
     "--max-requests", "1000",
     "--max-requests-jitter", "50",
     "--access-logfile", "-",
     "--error-logfile", "-",
     "app:create_app()"]
