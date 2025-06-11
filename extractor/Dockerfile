# Use a specific Python slim image
FROM python:3.13-slim

# Add OpenContainers labels
LABEL org.opencontainers.image.source="https://github.com/zchryr/vitalis"

# Set working directory
WORKDIR /extractor

# Update and upgrade system packages, install build tools, then clean up
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends gcc build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Copy requirements and install Python dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt \
    && rm -rf /root/.cache/pip/*

# Copy the extractor code into a subdirectory to make it a package
RUN mkdir -p /extractor/extractor
COPY . /extractor/extractor

# Set PYTHONPATH so extractor is discoverable
ENV PYTHONPATH=/extractor

# Copy entrypoint script and ensure it's executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set proper permissions
RUN chown -R appuser:appgroup /extractor

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

ENTRYPOINT ["/entrypoint.sh"]