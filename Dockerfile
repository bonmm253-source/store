# Use an official Python runtime as a parent image (Alpine for better compatibility on some networks)
FROM python:3.11-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies for Alpine
RUN apk update && \
    apk add --no-cache \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    gettext \
    curl \
    build-base \
    bash

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Make the start script executable
RUN chmod +x /app/scripts/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/scripts/start.sh"]

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Create a non-root user for security
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Make the start script executable
RUN chmod +x /app/scripts/start.sh

# Expose the port
EXPOSE 8000

# Start the application
CMD ["/app/scripts/start.sh"]
