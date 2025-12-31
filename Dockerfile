FROM python:3.10-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app

# System deps (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Create non-root user
RUN useradd -m appuser \
    && chown -R appuser:appuser /usr/src/app
USER appuser

# Fly expects 8080
EXPOSE 8080

# Use PORT env var (Fly sets this)
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8080"]
