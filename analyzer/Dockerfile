# Use a specific Python slim image
FROM python:3.13-slim

# Add OpenContainers labels
LABEL org.opencontainers.image.source="https://github.com/zchryr/vitalis"

# Set working directory
WORKDIR /analyzer

# Update and upgrade system packages, install build tools, then clean up
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy requirements and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache/pip/*

# Copy only the application code
COPY app.py ./
COPY README.md ./

# Set proper permissions
RUN chown -R appuser:appgroup /analyzer

# Switch to non-root user
USER appuser

# Set environment variables for hardening
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]