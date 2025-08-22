# Python 3.12 (>=3.10 per constraint)
FROM python:3.12-slim

# Env hygiene
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Create non-root user
RUN useradd -ms /bin/bash appuser

WORKDIR /app

# Install deps first (better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY app ./app

# Ownership to non-root
RUN chown -R appuser:appuser /app

# Switch to non-root
USER appuser

EXPOSE 5000

# Default command: run the Flask app
CMD ["python", "-m", "app.main"]
