# Use a more compatible Debian-based image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
# libcairo2-dev and pkg-config are required for pycairo (used by xhtml2pdf)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

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

# Use a shell script to handle migrations and startup
CMD ["/app/scripts/start.sh"]
