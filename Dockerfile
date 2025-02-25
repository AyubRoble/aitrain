# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    git

# Copy requirements first
COPY requirements.txt .

# Clear pip cache and install numpy first
RUN pip cache purge && \
    pip install --no-cache-dir numpy==1.21.6

# Then install other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT