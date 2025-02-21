FROM python:3.9

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements first (better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy all files
COPY . .

# Use shell form to allow environment variable substitution
CMD uvicorn main:app --host 0.0.0.0 --port $PORT