# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip

# Copy requirements first
COPY requirements.txt .

# Install numpy first separately
RUN pip install numpy==1.23.5

# Then install other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the code
COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT