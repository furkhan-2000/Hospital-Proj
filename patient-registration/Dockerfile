FROM python:3.11-slim

WORKDIR /app

ENV PATH="/home/appuser/.local/bin:${PATH}" \
    PYTHONPATH="/home/appuser/.local/lib/python3.11/site-packages:${PYTHONPATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app \
    FLASK_ENV=development \
    TMPDIR=/app/tmp \
    AUDIT_LOG_FILE=/app/logs/audit.log \
    PATIENT_DATA_DIR=/app/data/patient_data

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
       gcc \
       python3-dev \
       libpq-dev \
       curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN useradd -m appuser \
    && mkdir -p /app/data /app/logs /app/instance /app/uploads /app/tmp \
    && chown -R appuser:appuser /app /home/appuser \
    && chmod -R 755 /app \
    && chmod 1777 /app/tmp \
    && chmod 700 /app/instance

USER appuser

COPY --chown=appuser:appuser requirements.txt ./

RUN pip install --user --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .
COPY --chown=appuser:appuser ./app/static /app/static

EXPOSE 5003

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5003/health || exit 1

VOLUME /app/data /app/logs /app/uploads

CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]
