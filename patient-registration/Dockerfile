FROM python:3.11-slim

WORKDIR /app

# Environment variables - PATH FIRST!
ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    AUDIT_LOG_FILE=/app/logs/audit.log \
    PATIENT_DATA_DIR=/app/data/patient_data

# System dependencies - ADD PYTHON3-DEV
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       gcc \
       python3-dev \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user and dirs (existing setup is correct)
RUN useradd -m appuser \
    && mkdir -p /app/data /app/logs /app/instance /app/uploads \
    && chown -R appuser:appuser /app /home/appuser \
    && chmod -R 755 /app \
    && chmod 700 /app/instance

# Switch to non-root (you were already doing this correctly)
USER appuser

# Install requirements (existing command was correct)
COPY --chown=appuser:appuser requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=appuser:appuser . .

# Asset download
RUN chmod +x download_assets.sh && ./download_assets.sh

# Expose and healthcheck
EXPOSE 5003
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5003/health || exit 1

# Persist data and logs
VOLUME /app/data /app/logs /app/uploads

# Modified CMD for explicit execution
CMD ["python", "-m", "gunicorn", \
  "--bind", "0.0.0.0:5003", \
  "--workers", "2", \
  "--threads", "4", \
  "--timeout", "60", \
  "--max-requests", "1000", \
  "--max-requests-jitter", "50", \
  "--access-logfile", "-", \
  "--error-logfile", "-", \
  "app:create_app()"]