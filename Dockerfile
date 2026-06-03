# Optimized for GitHub Sync to Hugging Face
FROM python:3.11-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# System dependencies
USER root
RUN apt-get update && apt-get install -y build-essential libmagic1 && rm -rf /var/lib/apt/lists/*
USER user

# Copy from synchronized repo
COPY --chown=user python-api/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user python-api/ ./python-api/

# Run from where main.py is
WORKDIR /app/python-api

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
