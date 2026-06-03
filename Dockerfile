# National Cyber Crime Reporting System - AI Microservice
# Optimized for Hugging Face Spaces & Render

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for reportlab and python-magic
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY python-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY python-api/ ./python-api/

# Set working directory to where main.py is
WORKDIR /app/python-api

# Port 7860 is the default for Hugging Face Spaces
EXPOSE 7860

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
