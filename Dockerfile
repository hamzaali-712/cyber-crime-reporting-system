# Start from a Python 3.11 base
FROM python:3.11-slim

# Create a non-root user for security (Requirement for some HF spaces)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*
USER user

# Copy and install requirements
COPY --chown=user python-api/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application code
COPY --chown=user python-api/ ./python-api/

# Set working directory to where main.py is
WORKDIR /app/python-api

# Start the application using uvicorn
# Pointing to main:app and port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
