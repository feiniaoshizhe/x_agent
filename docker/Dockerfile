# Use official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install MySQL client libraries
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files and alembic configuration
COPY pyproject.toml README.md alembic.ini ./
COPY alembic ./alembic

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application code
COPY ./app ./app

# Copy environment configuration
COPY ./secret ./secret

# Copy static files (email templates)
COPY ./static ./static

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Startup command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
